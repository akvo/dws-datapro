import React, { useCallback, useMemo, useState } from "react";
import { Layout, Menu } from "antd";
import { store, config, api } from "../../lib";
import { useNavigate } from "react-router-dom";
import {
  UserOutlined,
  TableOutlined,
  DatabaseOutlined,
  DashboardOutlined,
  DownloadOutlined,
} from "@ant-design/icons";

const { Sider } = Layout;

const Sidebar = () => {
  const { user: authUser, administration } = store.useState((s) => s);
  const [selectedKey, setSelectedKey] = useState("");
  const [openKeys, setOpenKeys] = useState([]);
  const navigate = useNavigate();

  const { roles, checkApproverAccess } = config;
  const superAdminRole = roles.find((r) => r.id === authUser?.role_detail?.id);
  const isApprover = checkApproverAccess(authUser?.forms);

  const pageAccessToLabelAndUrlMapping = {
    user: { label: "Manage Platform Users", url: "/control-center/users" },
    approvers: {
      label: "Validation Tree",
      url: "/control-center/approvers/tree",
    },
    mobile: {
      label: "Manage Mobile Users",
      url: "/control-center/mobile-assignment",
    },
    data: { label: "Manage Data", url: "/control-center/data" },
    "master-data": [
      {
        label: "Administrative List",
        url: "/control-center/master-data/administration",
      },
      { label: "Attributes", url: "/control-center/master-data/attributes" },
      { label: "Entities", url: "/control-center/master-data/entities" },
      {
        label: "Entity Types",
        url: "/control-center/master-data/entity-types",
      },
      {
        label: "Organisations",
        url: "/control-center/master-data/organisations",
      },
    ],
    submissions: {
      label: "Manage Submissions",
      url: "/control-center/data/submissions",
    },
    approvals: {
      label: "Manage Approvals",
      url: "/control-center/approvals",
    },
  };

  const controlCenterToLabelMapping = useMemo(() => {
    const manageDataChildren = ["data", "submissions"];
    if (isApprover) {
      manageDataChildren.push("approvals");
    }
    const mapping = {
      "control-center": {
        label: "Control Center",
        icon: DashboardOutlined,
      },
      "manage-user": {
        label: "Users",
        icon: UserOutlined,
        childrenKeys: ["user", "approvers", "mobile"],
      },
      "manage-data": {
        label: "Data",
        icon: TableOutlined,
        childrenKeys: manageDataChildren,
      },
      "manage-master-data": {
        label: "Master Data",
        icon: DatabaseOutlined,
        childrenKeys: ["master-data"],
      },
      download: {
        label: "Downloads",
        icon: DownloadOutlined,
      },
    };
    return mapping;
  }, [isApprover]);

  const determineChildren = (key) => {
    const mapping = pageAccessToLabelAndUrlMapping[key];
    if (Array.isArray(mapping)) {
      return mapping.map((item, index) => ({
        key: key + "_" + index,
        ...item,
      }));
    }
    return [{ key, ...mapping }];
  };

  const createMenuItems = (controlCenterOrder, pageAccess) => {
    const menuItems = [];
    const controlCenterItem = controlCenterToLabelMapping["control-center"];
    const downloadItem = controlCenterToLabelMapping["download"];
    if (controlCenterItem) {
      menuItems.push({
        key: "control-center",
        icon: controlCenterItem.icon
          ? React.createElement(controlCenterItem.icon)
          : null,
        label: controlCenterItem.label,
        url: "/control-center",
      });
    }
    Object.keys(controlCenterToLabelMapping).forEach((orderKey) => {
      if (orderKey === "control-center" || orderKey === "download") {
        return;
      }

      const item = controlCenterToLabelMapping[orderKey];
      if (!item) {
        return;
      }

      const { label, icon, childrenKeys } = item;

      const shouldIncludeItem =
        controlCenterOrder.includes(orderKey) ||
        childrenKeys.some((childKey) => pageAccess.includes(childKey));

      if (shouldIncludeItem) {
        const children = childrenKeys
          .filter((key) => pageAccess.includes(key.split(/(\d+)/)[0]))
          .flatMap((key) => determineChildren(key, pageAccess));

        menuItems.push({
          key: orderKey,
          icon: icon ? React.createElement(icon) : null,
          label,
          children: children.length ? children : null,
        });
      }
    });
    if (downloadItem) {
      menuItems.push({
        key: "download",
        icon: downloadItem.icon ? React.createElement(downloadItem.icon) : null,
        label: downloadItem.label,
        url: "/downloads",
      });
    }

    return menuItems;
  };

  const usersMenuItem = createMenuItems(
    superAdminRole.control_center_order,
    superAdminRole.page_access
  );

  const findUrlByKey = (items, key) => {
    for (const item of items) {
      if (item.key === key) {
        return item.url;
      }
      if (item.children) {
        const url = findUrlByKey(item.children, key);
        if (url) {
          return url;
        }
      }
    }
  };

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

  const handleMenuClick = ({ key }) => {
    setSelectedKey(key);
    handleResetGlobalFilterState();
    const url = findUrlByKey(usersMenuItem, key);
    navigate(url);
  };

  const findKeyByUrl = useCallback((items, url) => {
    for (const item of items) {
      if (item.url === url) {
        return item.key;
      }
      if (url.split("/").length > 2) {
        const parentUrl = url.split("/").slice(0, 3).join("/");
        if (parentUrl === item.url) {
          return item.key;
        }
      }
      if (url.split("/").length > 3) {
        const parentUrl = url.split("/").slice(0, 4).join("/");
        if (parentUrl === item.url) {
          return item.key;
        }
      }
      if (item.children) {
        const key = findKeyByUrl(item.children, url);
        if (key) {
          return key;
        }
      }
    }
  }, []);

  return (
    <Sider className="site-layout-background">
      <Menu
        mode="inline"
        selectedKeys={[selectedKey]}
        openKeys={openKeys}
        style={{
          height: "100%",
          borderRight: 0,
        }}
        onSelect={handleMenuClick}
        onOpenChange={(newOpenKeys) => setOpenKeys(newOpenKeys)}
        items={usersMenuItem}
      />
    </Sider>
  );
};

export default Sidebar;
