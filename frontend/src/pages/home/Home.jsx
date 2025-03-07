import React, { useEffect } from "react";
import "./style.scss";
import { Collapse } from "antd";
import { HomeAdministrationChart } from "../../components";
import { HomeMap } from "./components";
import { queue } from "../../lib";
// const { TabPane } = Tabs;

// const partners = ["us-aid.png", "japan.png", "unicef.png"];
const { Panel } = Collapse;

export const Visuals = ({ current, mapValues, setMapValues }) => {
  return (
    <div>
      <div className="map-wrapper">
        {current?.maps?.form_id && (
          <HomeMap
            markerData={{ features: [] }}
            style={{ height: 532 }}
            current={current}
            mapValues={mapValues}
          />
        )}
      </div>
      <Collapse
        bordered={false}
        className="chart-collapse"
        style={{ display: "none" }}
      >
        <Panel
          header="Explore county-wise details"
          forceRender
          className="chart-panel"
        >
          <div className="chart-wrapper">
            {current?.charts?.map(
              (hc, hcI) =>
                (hc.type === "ADMINISTRATION" || hc.type === "CRITERIA") && (
                  <HomeAdministrationChart
                    key={`chart-${hc.id}-${hcI}`}
                    formId={hc.form_id}
                    setup={hc}
                    index={hcI + 1}
                    setMapValues={setMapValues}
                    identifier={current?.name}
                  />
                )
            )}
          </div>
        </Panel>
      </Collapse>
    </div>
  );
};

const Home = () => {
  // const { highlights } = window;
  // const [currentHighlight, setCurrentHighlight] = useState(highlights?.[0]);
  // const [mapValues, setMapValues] = useState([]);

  // const onTabClick = (active) => {
  //   setCurrentHighlight(highlights.find((x) => x.name === active));
  //   queue.update((q) => {
  //     q.next = 1;
  //     q.wait = null;
  //   });
  // };

  useEffect(() => {
    queue.update((q) => {
      q.next = 1;
      q.wait = null;
    });
  }, []);

  return <div id="home"></div>;
};

export default React.memo(Home);
