import React, {
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { Table, Button, Space, Spin, Alert } from "antd";
import { LoadingOutlined, HistoryOutlined } from "@ant-design/icons";
import { EditableCell } from "../../components";
import { api, QUESTION_TYPES, store, uiText } from "../../lib";
import { useNotification } from "../../util/hooks";
import { flatten, isEqual } from "lodash";
import { HistoryTable } from "../../components";
import { validateDependency } from "../../util";
import { AbilityContext } from "../../components/can";

const DataDetail = ({
  record,
  updater,
  updateRecord,
  setDeleteData,
  editedRecord,
  setEditedRecord,
  isPublic = false,
  isFullScreen = false,
}) => {
  const [dataset, setDataset] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [resetButton, setresetButton] = useState({});
  const pendingData = record?.pending_data?.created_by || false;
  const { notify } = useNotification();
  const { language, forms: allForms } = store.useState((s) => s);
  const { active: activeLang } = language;
  const text = useMemo(() => {
    return uiText[activeLang];
  }, [activeLang]);
  const ability = useContext(AbilityContext);

  const isEditor = ability.can("edit", "data");

  const questionGroups = useMemo(() => {
    return allForms.find((f) => f.id === record?.form)?.content?.question_group;
  }, [record?.form, allForms]);

  const updateCell = (key, parentId, value) => {
    setresetButton({ ...resetButton, [key]: true });
    let prev = JSON.parse(JSON.stringify(dataset));
    let hasEdits = false;
    prev = prev.map((qg) =>
      qg.id === parentId
        ? {
            ...qg,
            question: qg.question.map((qi) => {
              if (qi.id === key) {
                if (isEqual(qi.value, value)) {
                  if (qi.newValue) {
                    delete qi.newValue;
                  }
                } else {
                  qi.newValue = value;
                }
                const edited = !isEqual(qi.value, value);
                if (edited && !hasEdits) {
                  hasEdits = true;
                }
                return qi;
              }
              return qi;
            }),
          }
        : qg
    );
    const hasNewValue = prev
      .find((p) => p.id === parentId)
      ?.question?.some((q) => typeof q.newValue !== "undefined");
    setEditedRecord({ ...editedRecord, [record.id]: hasNewValue });
    setDataset(prev);
  };

  const resetCell = (key, parentId) => {
    let prev = JSON.parse(JSON.stringify(dataset));
    prev = prev.map((qg) =>
      qg.id === parentId
        ? {
            ...qg,
            question: qg.question.map((qi) => {
              if (qi.id === key) {
                delete qi.newValue;
              }
              return qi;
            }),
          }
        : qg
    );
    /**
     * Check whether it still has newValue or not
     * in all groups of questions
     */
    const hasNewValue = prev
      ?.flatMap((p) => p?.question)
      ?.find((q) => q?.newValue);
    setEditedRecord({ ...editedRecord, [record.id]: hasNewValue });
    setDataset(prev);
  };

  const handleSave = () => {
    const data = [];
    const formId = flatten(dataset.map((qg) => qg.question))[0].form;
    dataset.map((rd) => {
      rd.question.map((rq) => {
        if (rq.newValue || rq.newValue === 0) {
          let value = rq.newValue;
          if (rq.type === QUESTION_TYPES.number) {
            value =
              parseFloat(value) % 1 !== 0 ? parseFloat(value) : parseInt(value);
          }
          data.push({
            question: rq.id,
            value: value,
          });
        }
      });
    });
    setSaving(true);
    api
      .put(`form-data/${formId}?data_id=${record.id}`, data)
      .then(() => {
        notify({
          type: "success",
          message: "Data updated successfully",
        });
        updater(
          updateRecord === record.id
            ? false
            : updateRecord === null
            ? false
            : record.id
        );
        fetchData(record.id);
        const resetObj = {};
        data.map((d) => {
          resetObj[d.question] = false;
        });
        setresetButton({ ...resetButton, ...resetObj });
        setEditedRecord({ ...editedRecord, [record.id]: false });
      })
      .catch((e) => {
        console.error(e);
        notify({
          type: "error",
          message: "Could not update data",
        });
      })
      .finally(() => {
        setSaving(false);
      });
  };

  const fetchData = useCallback(
    (id) => {
      setLoading(true);
      api
        .get(`data/${id}`)
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
                    }))
                ),
              });
            }
          });

          setDataset(transformedData);
        })
        .catch((e) => {
          console.error(e);
        })
        .finally(() => {
          setLoading(false);
        });
    },
    [questionGroups]
  );

  useEffect(() => {
    if (record?.id && !dataset.length) {
      fetchData(record.id);
    }
  }, [record, dataset.length, fetchData]);

  const edited = useMemo(() => {
    return dataset.length
      ? flatten(dataset.map((qg) => qg.question)).findIndex(
          (fi) => fi.newValue
        ) > -1
      : false;
  }, [dataset]);

  return loading ? (
    <Space style={{ paddingTop: 18, color: "#9e9e9e" }} size="middle">
      <Spin indicator={<LoadingOutlined style={{ color: "#1b91ff" }} spin />} />
      <span>{text.loadingText}</span>
    </Space>
  ) : (
    <>
      <div className={`data-detail ${isFullScreen ? "full-screen" : ""}`}>
        {pendingData && (
          <Alert
            message={`Can't edit/update this data, because data in pending data by ${pendingData}`}
            type="warning"
          />
        )}
        {dataset.map((r, rI) => (
          <div className="pending-data-wrapper" key={rI}>
            <h3>{r.label}</h3>
            <Table
              pagination={false}
              dataSource={r.question}
              rowClassName={(record) => {
                const rowEdited =
                  (record.newValue || record.newValue === 0) &&
                  !isEqual(record.newValue, record.value)
                    ? "row-edited"
                    : "row-normal";
                return `expandable-row ${rowEdited}`;
              }}
              rowKey="id"
              columns={[
                {
                  title: text?.questionCol,
                  dataIndex: null,
                  width: "50%",
                  render: (_, row) =>
                    row.short_label ? row.short_label : row.label,
                  className: "table-col-question",
                },
                {
                  title: "Response",
                  render: (row) => (
                    <EditableCell
                      record={row}
                      parentId={row.question_group}
                      updateCell={updateCell}
                      resetCell={resetCell}
                      pendingData={pendingData}
                      isPublic={isPublic}
                      resetButton={resetButton}
                      readonly={!isEditor}
                    />
                  ),
                  width: "50%",
                },
                Table.EXPAND_COLUMN,
              ]}
              expandable={{
                expandIcon: ({ onExpand, record }) => {
                  if (!record?.history) {
                    return "";
                  }
                  return (
                    <HistoryOutlined
                      className="expand-icon"
                      onClick={(e) => onExpand(record, e)}
                    />
                  );
                },
                expandedRowRender: (record) => <HistoryTable record={record} />,
                rowExpandable: (record) => record?.history,
              }}
            />
          </div>
        ))}
      </div>
      {!isPublic && isEditor && (
        <div className="button-save">
          <Space>
            <Button
              type="primary"
              onClick={handleSave}
              disabled={!edited || saving}
              loading={saving}
              shape="round"
            >
              {text.saveEditButton}
            </Button>
            {ability.can("manage", "data") && (
              <Button
                type="danger"
                onClick={() => setDeleteData(record)}
                shape="round"
              >
                {text.deleteText}
              </Button>
            )}
          </Space>
        </div>
      )}
    </>
  );
};

export default React.memo(DataDetail);
