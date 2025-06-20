import React, { useMemo, useContext } from "react";
import { Tour } from "../../../components";
import { store, uiText } from "../../../lib";
import { AbilityContext } from "../../../components/can";

const ControlCenterTour = () => {
  const { language } = store.useState((s) => s);
  const { active: activeLang } = language;
  const text = useMemo(() => {
    return uiText[activeLang];
  }, [activeLang]);

  const ability = useContext(AbilityContext);

  const steps = [
    ...(ability?.can("manage", "data")
      ? [
          {
            image: "/assets/tour/control-center/1.png",
            title: "Manage Data",
            description: text.tourManageData,
          },
          {
            image: "/assets/tour/control-center/2.png",
            title: "Exports",
            description: text.tourExports,
          },
        ]
      : []),
    ...(ability?.can("manage", "form")
      ? [
          {
            image: "/assets/tour/control-center/3.png",
            title: "Data Uploads",
            description: text.tourDataUploads,
          },
        ]
      : []),
    ...(ability?.can("manage", "user")
      ? [
          {
            image: "/assets/tour/control-center/4.png",
            title: "User Management",
            description: text.tourUserManagement,
          },
        ]
      : []),
    ...(ability?.can("manage", "form")
      ? [
          {
            image: "/assets/tour/control-center/5.png",
            title: "Data Uploads Panel",
            description: text.tourDataUploadsPanel,
          },
        ]
      : []),
    ...(ability?.can("manage", "approvals")
      ? [
          {
            image: "/assets/tour/control-center/6.png",
            title: "Manage Approvals",
            description: text.tourApprovals,
          },
          {
            image: "/assets/tour/control-center/7.png",
            title: "Manage Approvers",
            description: text.tourApprovers,
          },
        ]
      : []),
  ];

  return <Tour steps={steps} />;
};

export default React.memo(ControlCenterTour);
