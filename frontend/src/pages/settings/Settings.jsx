/* TODO: DELETE COMPLETELY */
import React, { useMemo } from "react";
import "./style.scss";
import { Row, Col, Card, Button, Divider } from "antd";
import { store, uiText } from "../../lib";
import { Link } from "react-router-dom";
import { Breadcrumbs, DescriptionPanel } from "../../components";
import { Can } from "../../components/can";

const Settings = () => {
  const { language } = store.useState((s) => s);
  const { active: activeLang } = language;
  const text = useMemo(() => {
    return uiText[activeLang];
  }, [activeLang]);

  return (
    <div id="settings">
      <Row justify="space-between">
        <Breadcrumbs
          pagePath={[
            {
              title: text.settings,
              link: "/settings",
            },
          ]}
        />
      </Row>
      <DescriptionPanel
        description={text.settingsDescriptionPanel}
        title={text.settings}
      />
      <Divider />
      <Row gutter={[16, 16]}>
        <Can I="manage" a="master-data">
          <Col className="card-wrapper" span={12}>
            <Card bordered={false} hoverable>
              <div className="row">
                <div className="flex-1">
                  <h2>{text.orgPanelTitle}</h2>
                  <span>{text.orgPanelDescription}</span>
                  <Link
                    to="/control-center/master-data/organisations"
                    className="explore"
                  >
                    <Button type="primary" shape="round">
                      {text.orgPanelButton}
                    </Button>
                  </Link>
                </div>
                <div>
                  <img
                    src="/assets/personal-information.png"
                    width={100}
                    height={100}
                  />
                </div>
              </div>
            </Card>
          </Col>
        </Can>
      </Row>
    </div>
  );
};

export default React.memo(Settings);
