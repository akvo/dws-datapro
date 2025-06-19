import React, { Fragment, useMemo } from "react";
import "./style.scss";
import { Row, Col, Button } from "antd";
import { store, config, uiText, IS_SUPER_ADMIN } from "../../lib";
import { Link } from "react-router-dom";
import { PanelApprovals, PanelSubmissions } from "./components";
import { Breadcrumbs, DescriptionPanel } from "../../components";
import { ControlCenterTour } from "./components";

const ControlCenter = () => {
  const { user: authUser } = store.useState((s) => s);
  const { language } = store.useState((s) => s);

  const { active: activeLang } = language;

  const text = useMemo(() => {
    return uiText[activeLang];
  }, [activeLang]);

  const { roles, checkAccess, checkApproverAccess } = config;

  const panels = useMemo(() => {
    return [
      {
        key: "approvals",
        access: "approvals",
        render: (
          <div className="table-wrapper">
            <Col key="approvals-panel" span={24}>
              <PanelApprovals />
            </Col>
          </div>
        ),
      },
      {
        key: "submission",
        access: "form",
        render: (
          <div className="table-wrapper">
            <Col key="submission-panel" span={24}>
              <PanelSubmissions />
            </Col>
          </div>
        ),
      },
    ];
  }, []);

  const selectedPanels = useMemo(() => {
    if (authUser?.roles?.length === 0 && !authUser?.is_superuser) {
      return [];
    }
    // TODO: Implement RBAC
    const panelOrder = roles.find(
      (r) => r.id === IS_SUPER_ADMIN
    )?.control_center_order;

    if (!panelOrder) {
      return [];
    }

    const filteredAndOrderedPanels = panelOrder
      .map((orderKey) =>
        panels.find(
          (panel) =>
            panel.key === orderKey && checkAccess(authUser.roles, panel.access)
        )
      )
      .filter((panel) => panel)
      .filter(
        (panel) =>
          (panel.access === "approvals" &&
            checkApproverAccess(authUser?.forms)) ||
          panel.access !== "approvals"
      );

    return filteredAndOrderedPanels;
  }, [panels, roles, checkAccess, checkApproverAccess, authUser]);

  return (
    <>
      <div className="description-container">
        <Row justify="space-between">
          <Breadcrumbs
            pagePath={[
              {
                title: text.controlCenter,
                link: "/control-center",
              },
            ]}
          />
          <ControlCenterTour />
        </Row>
        <DescriptionPanel description={text.ccDescriptionPanel} />

        <div className="profile-container">
          <h2>
            {window.appConfig.name} {text.controlCenter}
          </h2>
          <div className="profle-wrapper">
            <img src="/assets/profile.png" />
            <div>
              <h2>{`${text.helloText} ${authUser?.name}`},</h2>
              <p>
                {authUser?.role?.value} | {authUser.designation?.name}
                {authUser.organisation?.name &&
                  `- ${authUser.organisation?.name}`}
              </p>
              <p>
                {`${text.lastLoginLabel}: `}
                {new Date(authUser?.last_login * 1000)
                  .toISOString()
                  .replace("T", " ")
                  .slice(0, 19)}
              </p>
            </div>
          </div>
        </div>
      </div>
      <div className="table-section">
        <Row gutter={[16, 32]}>
          {selectedPanels.map((panel, index) => {
            if (panel?.render) {
              return <Fragment key={index}>{panel.render}</Fragment>;
            }
            const cardOnly = selectedPanels.filter((x) => !x?.render);
            const isFullWidth =
              cardOnly.length === 1 ||
              (selectedPanels.length % 2 === 1 &&
                selectedPanels.length - 1 === index);
            return (
              <Col
                className="card-wrapper"
                span={isFullWidth ? 24 : 12}
                key={panel.key}
              >
                <div hoverable>
                  <div className="row">
                    <div className="flex-1">
                      <h2>{panel?.title}</h2>
                      <span>{panel?.description}</span>
                      <Link to={panel?.link} className="explore">
                        <Button type="primary" shape="round">
                          {panel?.buttonLabel}
                        </Button>
                      </Link>
                    </div>
                    <div>
                      <img src={panel?.image} width={100} height={100} />
                    </div>
                  </div>
                </div>
              </Col>
            );
          })}
        </Row>
      </div>
    </>
  );
};

export default ControlCenter;
