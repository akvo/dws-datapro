import React, { useContext, useMemo } from "react";
import { Layout, Menu } from "antd";
import { store, uiText } from "../../lib";
import api from "../../lib/api";
import { useNavigate } from "react-router-dom";
import {
  UserOutlined,
  TableOutlined,
  DatabaseOutlined,
  DashboardOutlined,
  DownloadOutlined,
} from "@ant-design/icons";
import { AbilityContext, Can } from "../can";

const { Sider } = Layout;

const Sidebar = () => {
  const { user: authUser, administration, language } = store.useState((s) => s);
  const navigate = useNavigate();

  const { active: activeLang } = language || { active: "en" };
  const text = useMemo(() => {
    return uiText[activeLang] || uiText.en;
  }, [activeLang]);

  const ability = useContext(AbilityContext);

  const handleResetGlobalFilterState = async () => {
    // reset global filter store when moving page on sidebar click
    store.update((s) => {
      s.filters = {
        trained: null,
        role: null,
        organisation: null,
        query: null,
        attributeType: null,
        entityType: [],
      };
    });
    if (authUser?.administration?.id && administration?.length > 1) {
      try {
        const { data: apiData } = await api.get(
          `administration/${authUser.administration.id}`
        );
        store.update((s) => {
          s.administration = [apiData];
        });
      } catch (error) {
        console.error(error);
      }
    }
  };

  const handleMenuClick = ({ item }) => {
    // Get the URL from the menu item
    const url = item.props?.["data-url"];
    // Reset global filter state
    handleResetGlobalFilterState();
    // Navigate to the URL
    navigate(url);
  };

  return (
    <Sider className="site-layout-background">
      <Menu
        mode="inline"
        style={{
          height: "100%",
          borderRight: 0,
        }}
        onClick={handleMenuClick}
      >
        {/* Control Center */}

        <Menu.Item
          key="menu-control-center"
          icon={<DashboardOutlined />}
          data-url="/control-center"
        >
          {text.menuControlCenter}
        </Menu.Item>

        {/* Users SubMenu */}
        <Menu.SubMenu
          key="manage-user"
          icon={<UserOutlined />}
          title={text.menuUsers}
        >
          {/* Wrap each menu item explicitly with a unique key for Can */}
          <Can I="manage" a="user" key="can-platform-users">
            <Menu.Item
              key="menu-platform-users"
              data-url="/control-center/users"
            >
              {text.menuManagePlatformUsers}
            </Menu.Item>
          </Can>
          <Menu.Item
            key="menu-approvers"
            data-url="/control-center/approvers/tree"
          >
            {text.menuValidationTree}
          </Menu.Item>
          {ability.can("read", "mobile") && (
            <Menu.Item
              key="menu-mobile-users"
              data-url="/control-center/mobile-assignment"
            >
              {text.menuManageMobileUsers}
            </Menu.Item>
          )}
          {ability.can("manage", "roles") && (
            <Menu.Item key="menu-roles" data-url="/control-center/roles">
              {text.menuManageRoles}
            </Menu.Item>
          )}
        </Menu.SubMenu>

        {/* Data SubMenu */}
        <Menu.SubMenu
          key="manage-data"
          icon={<TableOutlined />}
          title={text.menuData}
        >
          <Menu.Item key="menu-manage-data" data-url="/control-center/data">
            {text.menuManageData}
          </Menu.Item>

          {ability.can("manage", "submissions") && (
            <Menu.Item
              key="menu-submissions"
              data-url="/control-center/data/submissions"
            >
              {text.menuPendingSubmissions}
            </Menu.Item>
          )}

          {ability.can("manage", "approvals") && (
            <Menu.Item
              key="menu-approvals"
              data-url="/control-center/approvals"
            >
              {text.menuApprovals}
            </Menu.Item>
          )}
        </Menu.SubMenu>

        {/* Master Data SubMenu */}
        <Can I="manage" a="master-data" key="can-master-data">
          <Menu.SubMenu
            key="manage-master-data"
            icon={<DatabaseOutlined />}
            title={text.menuMasterData}
          >
            <Menu.Item
              key="menu-master-data-administration"
              data-url="/control-center/master-data/administration"
            >
              {text.menuAdministrativeList}
            </Menu.Item>
            <Menu.Item
              key="menu-master-data-attributes"
              data-url="/control-center/master-data/attributes"
            >
              {text.menuAttributes}
            </Menu.Item>
            <Menu.Item
              key="menu-master-data-entities"
              data-url="/control-center/master-data/entities"
            >
              {text.menuEntities}
            </Menu.Item>
            <Menu.Item
              key="menu-master-data-entity-types"
              data-url="/control-center/master-data/entity-types"
            >
              {text.menuEntityTypes}
            </Menu.Item>
            <Menu.Item
              key="menu-master-data-organisations"
              data-url="/control-center/master-data/organisations"
            >
              {text.menuOrganisations}
            </Menu.Item>
          </Menu.SubMenu>
        </Can>

        {/* Downloads */}
        {ability.can("read", "downloads") && (
          <Menu.Item
            key="menu-downloads"
            icon={<DownloadOutlined />}
            data-url="/downloads"
          >
            {text.menuDownloads}
          </Menu.Item>
        )}
      </Menu>
    </Sider>
  );
};

export default Sidebar;
