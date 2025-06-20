import React, { useMemo, useContext } from "react";
import { Tour } from "../../../components";
import { store, uiText } from "../../../lib";
import { AbilityContext } from "../../../components/can";

const ProfileTour = () => {
  const { language } = store.useState((s) => s);
  const { active: activeLang } = language;
  const text = useMemo(() => {
    return uiText[activeLang];
  }, [activeLang]);

  const ability = useContext(AbilityContext);

  const steps = [
    {
      image: "/assets/tour/profile/1.png",
      title: "Control Center",
      description: text.tourControlCenter,
    },
    ...(ability?.can("manage", "form")
      ? [
          {
            image: "/assets/tour/profile/2.png",
            title: "Data Uploads",
            description: text.tourDataUploads,
          },
        ]
      : []),
    ...(ability?.can("manage", "approvals")
      ? [
          {
            image: "/assets/tour/profile/3.png",
            title: "Manage Approvals",
            description: text.tourApprovals,
          },
          {
            image: "/assets/tour/profile/4.png",
            title: "Manage Approvers",
            description: text.tourApprovers,
          },
        ]
      : []),
  ];

  return <Tour steps={steps} />;
};

export default React.memo(ProfileTour);
