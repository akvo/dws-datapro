export const transformRawData = (questionGroups = [], answers = []) => {
  const data = questionGroups
    .map((qg) => {
      if (qg?.repeatable) {
        const requiredQuestion = qg.question.find((q) => q.required);
        const totalRepeat =
          answers.filter((d) => d.question === requiredQuestion?.id)?.length ||
          1;
        return Array.from({ length: totalRepeat }, (_, i) => ({
          ...qg,
          id: `${qg.id}-${i}`,
          label: `${qg.label} #${i + 1}`,
          question: qg.question.map((q) => {
            const findValue = answers.find(
              (d) => d.question === q.id && d.index === i
            )?.value;
            const findOldValue = answers.find(
              (d) => d.question === q.id && d.index === i
            )?.last_value;
            return {
              ...q,
              value: findValue || findValue === 0 ? findValue : null,
              lastValue:
                findOldValue || findOldValue === 0 ? findOldValue : null,
              history:
                answers.find((d) => d.question === q.id && d.index === i)
                  ?.history || false,
            };
          }),
        }));
      }
      return [
        {
          ...qg,
          question: qg.question.map((q) => {
            const findValue = answers.find((d) => d.question === q.id)?.value;
            const findOldValue = answers.find(
              (d) => d.question === q.id
            )?.last_value;
            return {
              ...q,
              value: findValue || findValue === 0 ? findValue : null,
              lastValue:
                findOldValue || findOldValue === 0 ? findOldValue : null,
              history:
                answers.find((d) => d.question === q.id)?.history || false,
            };
          }),
        },
      ];
    })
    .flat();
  return data;
};
