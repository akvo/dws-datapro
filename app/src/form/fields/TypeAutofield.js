import React, { useEffect, useState } from 'react';
import { View } from 'react-native';
import { Input } from '@rneui/themed';
import * as Sentry from '@sentry/react-native';

import { FieldLabel } from '../support';
import styles from '../styles';
import { FormState } from '../../store';

const sanitize = [
  {
    prefix: /return fetch|fetch/g,
    re: /return fetch(\(.+)\} +|fetch(\(.+)\} +/,
    log: 'Fetch is not allowed.',
  },
];

const checkDirty = (fnString) =>
  sanitize.reduce((prev, sn) => {
    const dirty = prev.match(sn.re);
    if (dirty) {
      return prev.replace(sn.prefix, '').replace(dirty[1], `console.error("${sn.log}");`);
    }
    return prev;
  }, fnString);

// convert fn string to array
const fnToArray = (fnString) => {
  // First handle hex color codes by temporarily replacing them
  const hexColorPattern = /"#[0-9A-Fa-f]{6}"/g;
  const hexColors = [];
  let modifiedString = fnString;

  // Extract and replace hex colors with placeholders
  let index = 0;
  let match = hexColorPattern.exec(fnString);
  while (match !== null) {
    const placeholder = `__HEX_COLOR_${index}__`;
    hexColors.push({ placeholder, value: match[0] });
    modifiedString = modifiedString.replace(match[0], placeholder);
    index += 1;
    match = hexColorPattern.exec(fnString);
  }

  // Normal tokenization
  const regex =
    // eslint-disable-next-line no-useless-escape
    /\#\d+|[(),?;&.'":()+\-*/.!]|<=|<|>|>=|!=|==|[||]{2}|=>|__HEX_COLOR_[0-9]+__|\w+| /g;
  const tokens = modifiedString.match(regex) || [];

  // Restore hex colors
  return tokens.map((token) => {
    const hexColor = hexColors.find((hc) => hc.placeholder === token);
    return hexColor ? hexColor.value : token;
  });
};

const handeNumericValue = (val) => {
  const regex = /^"\d+"$|^\d+$/;
  const isNumeric = regex.test(val);
  if (isNumeric) {
    return String(val).trim().replace(/['"]/g, '');
  }
  return val;
};

const generateFnBody = (fnMetadata, values, questions = []) => {
  if (!fnMetadata) {
    return false;
  }

  // Create a map of question names to IDs for faster lookup
  const questionMap = {};
  if (questions && questions.length) {
    questions.forEach((q) => {
      if (q.name && q.id) {
        questionMap[q.name] = q.id;
      }
    });
  }

  let defaultVal = null;
  // Replace variables with numeric placeholders
  let processedString = fnMetadata;
  // Iterate over keys of the values object and replace placeholders with '0'
  Object.keys(values).forEach((key) => {
    processedString = processedString.replace(new RegExp(`#${key}#`, 'g'), '0');
  });

  // Check if the processed string matches the regular expression
  const validNumericRegex = /^[\d\s+\-*/().]*$/;
  if (!validNumericRegex.test(processedString)) {
    // update defaultVal into empty string for non numeric equation
    defaultVal = fnMetadata.includes('!') ? String(null) : '';
  }

  const fnMetadataTemp = fnToArray(fnMetadata);

  // generate the fnBody
  const fnBody = fnMetadataTemp.map((f) => {
    // First check for literal hex color codes in quotes - don't process them
    if (f.startsWith('"#') && f.endsWith('"') && /^"#[0-9A-Fa-f]{6}"$/.test(f)) {
      return f; // Return hex color as-is
    }
    // Check if the token is a number or a string
    if (questionMap?.[f]) {
      let val = values?.[questionMap[f]];

      if (!val && val !== 0) {
        return defaultVal;
      }
      if (typeof val === 'object') {
        if (Array.isArray(val)) {
          val = val.join(',');
        } else if (val?.lat) {
          val = `${val.lat},${val.lng}`;
        } else {
          val = defaultVal;
        }
      }
      if (typeof val === 'number') {
        val = Number(val);
      }
      if (typeof val === 'string') {
        val = `"${val}"`;
      }

      return val;
    }
    return f;
  });

  // all fn conditions meet, return generated fnBody
  if (!fnBody.filter((x) => !x).length) {
    return fnBody
      .map(handeNumericValue)
      .join('')
      .replace(/(?:^|\s)\.includes\(['"][^'"]+['"]\)/g, "''$1")
      .replace(/''\s*\./g, "''.");
  }

  // remap fnBody if only one fnBody meet the requirements
  return fnBody
    .filter((x) => x)
    .map(handeNumericValue)
    .join('')
    .replace(/(?:^|\s)\.includes\(['"][^'"]+['"]\)/g, " ''$&")
    .replace(/''\s*\./g, "''.");
};

const fixIncompleteMathOperation = (expression) => {
  // Regular expression to match incomplete math operations
  const incompleteMathRegex = /[+\-*/]\s*$/;

  // Check if the input ends with an incomplete math operation
  if (incompleteMathRegex.test(expression)) {
    // If the expression ends with '+' or '-', append '0' to complete the operation
    if (expression.trim().endsWith('+') || expression.trim().endsWith('-')) {
      return `${expression.trim()}0`;
    }
    // If the expression ends with '*' or '/', it's safer to remove the operator
    if (expression.trim().endsWith('*') || expression.trim().endsWith('/')) {
      return expression.trim().slice(0, -1);
    }
  }
  return expression;
};

const strToFunction = (fnString, values, questions = []) => {
  try {
    const fnStr = checkDirty(fnString);
    const fnBody = fixIncompleteMathOperation(generateFnBody(fnStr, values, questions));
    // eslint-disable-next-line no-new-func
    return new Function(`return ${fnBody}`);
  } catch {
    return null;
  }
};

const TypeAutofield = ({
  keyform,
  id,
  label,
  fn,
  tooltip = null,
  displayOnly = false,
  questions = [],
  value: autofieldValue = null,
}) => {
  const [value, setValue] = useState(null);
  const [fieldColor, setFieldColor] = useState(null);
  const { fnString: nameFnString, fnColor } = fn;

  useEffect(() => {
    const unsubsValues = FormState.subscribe(({ currentValues, surveyStart }) => {
      if (!surveyStart) {
        /**
         * When the survey session ends, `fnString` will not be re-executed.
         * */
        return;
      }
      try {
        // Extract all questions from the question groups
        const allQuestions = questions.flatMap((q) => q.question);

        // Pass the original fnString and allQuestions to strToFunction
        const automateValue = strToFunction(nameFnString, currentValues, allQuestions);
        if (typeof automateValue === 'function') {
          const answer = automateValue();
          if (answer !== value && (answer || answer === 0)) {
            setValue(answer);

            // Handle fnColor - supports both string-based function and object lookup
            if (typeof fnColor === 'string') {
              // Use the original fnColor string with allQuestions
              const fnColorFunction = strToFunction(fnColor, currentValues, allQuestions);
              if (typeof fnColorFunction === 'function') {
                const fnColorValue = fnColorFunction();
                if (fnColorValue && fnColorValue !== fieldColor) {
                  setFieldColor(fnColorValue);
                }
              }
            } else if (typeof fnColor === 'object' && fnColor?.[answer]) {
              setFieldColor(fnColor[answer]);
            } else {
              setFieldColor(null);
            }
          }
        }
      } catch (error) {
        Sentry.captureMessage(`[TypeAutofield] question ID: ${id}`);
        Sentry.captureException(error);
      }
    });

    return () => {
      unsubsValues();
    };
  }, [fnColor, nameFnString, id, value, fieldColor, questions]);

  useEffect(() => {
    if (value !== null && value !== autofieldValue && !displayOnly) {
      FormState.update((s) => {
        s.currentValues[id] = value;
      });
    }
  }, [value, id, autofieldValue, displayOnly]);

  return (
    <View testID="type-autofield-wrapper">
      <FieldLabel keyform={keyform} name={label} tooltip={tooltip} />
      <Input
        inputContainerStyle={{
          ...styles.autoFieldContainer,
          backgroundColor: fieldColor || styles.autoFieldContainer.backgroundColor,
        }}
        value={value || value === 0 ? String(value) : null}
        testID="type-autofield"
        multiline
        numberOfLines={2}
        disabled
        style={{
          fontWeight: 'bold',
          opacity: 1,
        }}
      />
    </View>
  );
};

export default TypeAutofield;
