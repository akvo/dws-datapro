import React, { useCallback, useMemo } from "react";
import PropTypes from "prop-types";
import { Row, Col, Space, Button, Dropdown } from "antd";
import { UserOutlined } from "@ant-design/icons";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { config, store, uiText } from "../../lib";
import { eraseCookieFromAllPaths } from "../../util/date";

const Header = ({ className = "header", ...props }) => {
  const { isLoggedIn, user } = store.useState();
  const navigate = useNavigate();
  const location = useLocation();
  const { language } = store.useState((s) => s);
  const { active: activeLang } = language;
  const text = useMemo(() => {
    return uiText[activeLang];
  }, [activeLang]);
  const dashboards = window?.powerBIDashboard;

  const signOut = useCallback(async () => {
    eraseCookieFromAllPaths("AUTH_TOKEN");
    store.update((s) => {
      s.isLoggedIn = false;
      s.user = null;
    });
    navigate("login");
  }, [navigate]);

  const accessUserMenu = useMemo(() => {
    const userMenu = [
      {
        key: "controlCenter",
        label: (
          <Link
            key="controlCenter"
            className="usermenu-menu-item"
            to="/control-center"
          >
            {text?.controlCenter}
          </Link>
        ),
      },
      {
        key: "profile",
        label: (
          <Link
            key="profile"
            className="usermenu-menu-item"
            to="/control-center/profile"
          >
            {text?.myProfile}
          </Link>
        ),
      },
      {
        key: "signOut",
        danger: true,
        label: (
          <a
            key="signOut"
            className="usermenu-menu-item"
            onClick={() => {
              signOut();
            }}
          >
            {text?.signOut}
          </a>
        ),
      },
    ];
    if (!config.checkAccess(user?.role_detail, "control-center")) {
      return userMenu.filter((menu) => menu.key !== "controlCenter");
    }
    return userMenu;
  }, [text, user, signOut]);

  const DashboardMenu = useMemo(() => {
    return dashboards?.map((d) => {
      return {
        key: d.name,
        label: (
          <Link
            key={`${d.name}`}
            to={`/${d.page}/${d.path}`}
            className="dropdown-menu-item"
          >
            {d.name}
          </Link>
        ),
      };
    });
  }, [dashboards]);

  return (
    <Row
      className={className}
      align="middle"
      justify="space-between"
      {...props}
    >
      <Col>
        <div className="logo">
          <Link to="/">
            <div className="logo-wrapper">
              <img
                className="small-logo"
                src={config.siteLogo}
                alt={config.siteLogo}
              />
            </div>
          </Link>
        </div>
      </Col>
      {!location.pathname.includes("/report/") && (
        <Col>
          <div className="navigation">
            <Space>
              {/* old dashboard */}
              {/* <Link to="/data/visualisation">{text?.dashboards}</Link> */}
              {/* new dashboard
              <Link className="dev" to="/reports">
                {text?.reports}
              </Link>
              <Dropdown menu={{ items: DashboardMenu }}>
                <a
                  className="ant-dropdown-link"
                  onClick={(e) => {
                    e.preventDefault();
                  }}
                >
                  {text?.dashboards}
                  <FaChevronDown />
                </a>
              </Dropdown>
               */}
              {/* <a className="dev">Monitoring</a> */}
              {/* <Link className="dev" to="/how-we-work">
              How We Work
            </Link> */}
              {/* <Link className="dev" to="/news-events">
                {text?.newsEvents}
              </Link> */}
            </Space>
          </div>
          <div className="account">
            {isLoggedIn ? (
              <Dropdown menu={{ items: accessUserMenu }}>
                <a
                  className="ant-dropdown-link"
                  onClick={(e) => {
                    e.preventDefault();
                  }}
                >
                  {user?.name || ""}
                  <span className="role">, {user?.role?.value || ""}</span>
                  <span className="icon">
                    <UserOutlined />
                  </span>
                </a>
              </Dropdown>
            ) : (
              <Link to={"/login"}>
                <Button type="primary" shape="round">
                  {text?.login}
                </Button>
              </Link>
            )}
          </div>
        </Col>
      )}
    </Row>
  );
};

Header.propTypes = {
  className: PropTypes.string,
};

export default Header;
