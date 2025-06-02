import React, { useEffect, useMemo, useState } from "react";
import SubmissionEditing from "./SubmissionEditing";
import { api, QUESTION_TYPES, store, uiText } from "../../lib";
import { isEqual, flatten, last } from "lodash";
import { useNotification } from "../../util/hooks";
import { validateDependency } from "../../util";

const BatchDetail = ({
  expanded,
  setReload,
  deleting,
  handleDelete,
  editedRecord,
  setEditedRecord,
}) => {
  const [dataLoading, setDataLoading] = useState(true);
  const [saving, setSaving] = useState(null);
  const [rawValue, setRawValue] = useState(null);
  const [resetButton, setresetButton] = useState({});
  const { notify } = useNotification();
  const language = store.useState((s) => s.language);
  const { active: activeLang } = language;

  const text = useMemo(() => {
    return uiText[activeLang];
  }, [activeLang]);

  const questionGroups = window.forms
    .find((f) => f.id === expanded.form)
    ?.content?.question_group?.filter(
      (qg) =>
        qg.question?.length ===
        qg.question.filter((q) => !q?.display_only).length
    );

  useEffect(() => {
    if (questionGroups && dataLoading) {
      api
        .get(`pending-data/${expanded.id}`)
        .then((res) => {
          // Process the data differently for repeatable and non-repeatable question groups
          const transformedData = [];

          // Process each question group
          questionGroups.forEach((qg) => {
            if (qg?.repeatable) {
              // For repeatable groups, we need to find how many instances of each question exist
              // Group the response data by question ID
              const questionOccurrences = {};
              qg.question.forEach((q) => {
                // Find all responses for this question
                const responses = res.data.filter((r) => r.question === q.id);
                // Track the maximum number of responses for any question in this group
                const count = responses.length;
                questionOccurrences[q.id] = count;
              });

              // Find the maximum count of responses for any question in this group
              const maxCount = Math.max(
                ...Object.values(questionOccurrences),
                0
              );

              // Create copies of the question group for each response instance
              for (let i = 0; i < maxCount; i++) {
                const questionGroupCopy = {
                  ...qg,
                  label: `${qg.label} #${i + 1}`,
                };
                questionGroupCopy.question = qg.question
                  .filter((q) => {
                    if (q?.dependency) {
                      const isValid = q.dependency.some((d) => {
                        const value = res.data.filter(
                          (r) => r.question === d.id
                        )?.[i]?.value;
                        return validateDependency(d, value);
                      });
                      return isValid;
                    }
                    return q;
                  })
                  .map((q) => {
                    // Get all responses for this question
                    const responses = res.data.filter(
                      (r) => r.question === q.id
                    );

                    // If the question has a dependency, then get the response
                    // for the current instance (i) or the first instance (0)
                    let response = responses?.find((r) => r?.index === i);
                    if (q?.dependency) {
                      response = responses?.[i] ||
                        responses?.[0] || {
                          value: null,
                          history: false,
                        };
                    }
                    if (q?.type === QUESTION_TYPES.attachment) {
                      response = responses.find((r) =>
                        r.value?.includes(`${q.id}-${i}`)
                      );
                    }
                    return {
                      ...q,
                      id: i > 0 ? `${q.id}-${i}` : q.id, // Add suffix for duplicate questions
                      value: response?.value,
                      history: response?.history || false,
                      lastValue: response?.last_value,
                    };
                  });
                transformedData.push(questionGroupCopy);
              }
            } else {
              // For non-repeatable groups, process as before
              transformedData.push({
                ...qg,
                question: qg.question.flatMap((q) =>
                  res.data
                    .filter((r) => r.question === q.id)
                    .map((d, dx) => ({
                      ...q,
                      id: dx ? `${q.id}-${dx}` : q.id,
                      value: d?.value,
                      history: d?.history || false,
                      lastValue: d?.last_value,
                    }))
                ),
              });
            }
          });

          setRawValue({ ...expanded, data: transformedData, loading: false });
        })
        .catch((e) => {
          console.error(e);
          setRawValue({ ...expanded, data: [], loading: false });
        })
        .finally(() => {
          setDataLoading(false);
        });
    }
  }, [expanded, questionGroups, dataLoading]);

  const handleSave = (data) => {
    setSaving(data.id);
    const formData = [];
    data.data.map((rd) => {
      rd.question.map((rq) => {
        if (
          (rq.newValue || rq.newValue === 0) &&
          !isEqual(rq.value, rq.newValue)
        ) {
          let value = rq.newValue;
          if (rq.type === QUESTION_TYPES.number) {
            value =
              parseFloat(value) % 1 !== 0 ? parseFloat(value) : parseInt(value);
          }
          formData.push({
            question: rq.id,
            value: value,
          });
          delete rq.newValue;
        }
      });
    });
    api
      .put(
        `form-pending-data/${expanded.form}?pending_data_id=${data.id}`,
        formData
      )
      .then(() => {
        setReload(data.id);
        const resetObj = {};
        formData.map((data) => {
          resetObj[data.question] = false;
        });
        setresetButton({ ...resetButton, ...resetObj });
        setEditedRecord({ ...editedRecord, [expanded.id]: false });
        notify({
          type: "success",
          message: text.successDataUpdated,
        });
      })
      .catch((e) => {
        console.error(e);
      })
      .finally(() => {
        setSaving(null);
      });
  };

  const updateCell = (key, parentId, value) => {
    setresetButton({ ...resetButton, [key]: true });
    let hasEdits = false;
    const data = rawValue.data.map((rd) => ({
      ...rd,
      question: rd.question.map((rq) => {
        if (rq.id === key && expanded.id === parentId) {
          if (isEqual(rq.value, value)) {
            if (rq.newValue) {
              delete rq.newValue;
            }
          } else {
            rq.newValue = value;
          }
          const edited = !isEqual(rq.value, value);
          if (edited && !hasEdits) {
            hasEdits = true;
          }
          return rq;
        }
        if (
          (rq.newValue || rq.newValue === 0) &&
          !isEqual(rq.value, rq.newValue) &&
          !hasEdits
        ) {
          hasEdits = true;
        }
        return rq;
      }),
    }));
    const hasNewValue = data.some((d) => {
      return d.question?.some((q) => {
        return typeof q.newValue !== "undefined";
      });
    });
    setEditedRecord({ ...editedRecord, [expanded.id]: hasNewValue });
    setRawValue({
      ...rawValue,
      data,
      edited: hasEdits,
    });
  };

  const resetCell = (key, parentId) => {
    const prev = JSON.parse(JSON.stringify(rawValue));
    let hasEdits = false;
    const data = prev.data.map((rd) => ({
      ...rd,
      question: rd.question.map((rq) => {
        if (rq.id === key && expanded.id === parentId) {
          delete rq.newValue;
          return rq;
        }
        if (
          (rq.newValue || rq.newValue === 0) &&
          !isEqual(rq.value, rq.newValue) &&
          !hasEdits
        ) {
          hasEdits = true;
        }
        return rq;
      }),
    }));
    /**
     * Check whether it still has newValue or not
     * in all groups of questions
     */
    const hasNewValue = data
      ?.flatMap((d) => d?.question)
      ?.find((q) => q?.newValue);
    setEditedRecord({ ...editedRecord, [expanded.id]: hasNewValue });
    setRawValue({
      ...prev,
      data,
      edited: hasEdits,
    });
  };

  const isEdited = () => {
    return (
      !!flatten(rawValue?.data?.map((g) => g.question))?.filter(
        (d) => (d.newValue || d.newValue === 0) && !isEqual(d.value, d.newValue)
      )?.length || false
    );
  };

  if (!rawValue) {
    return <div>{text.loadingText}</div>;
  }

  return (
    <SubmissionEditing
      expanded={rawValue}
      updateCell={updateCell}
      resetCell={resetCell}
      handleSave={handleSave}
      handleDelete={handleDelete}
      saving={saving}
      dataLoading={dataLoading}
      isEdited={isEdited}
      isEditable={true}
      deleting={deleting}
      resetButton={resetButton}
    />
  );
};

export default BatchDetail;
