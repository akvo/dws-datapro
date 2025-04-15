import "@testing-library/jest-dom";
import geo from "../geo";

describe("geo", () => {
  test("test if getBounds when empty array is passed as administration", () => {
    const expectedResult = {
      bbox: [
        [NaN, NaN],
        [NaN, NaN],
      ],
      coordinates: [NaN, NaN],
    };
    expect(geo.getBounds([])).toEqual(expectedResult);
  });

  test("test if getBounds with an administration", () => {
    const administration = [
      {
        childLevelName: "ADM_1",
        children: [
          {
            full_name: "ADM_0A|ADM_1A",
            id: 2,
            level: 1,
            name: "ADM_1A",
            parent: 1,
            path: "1.",
          },
          {
            full_name: "ADM_0A|ADM_1B",
            id: 3,
            level: 1,
            name: "ADM_1B",
            parent: 1,
            path: "1.",
          },
          {
            full_name: "ADM_0A|ADM_1C",
            id: 4,
            level: 1,
            name: "ADM_1C",
            parent: 1,
            path: "1.",
          },
        ],
        full_name: "ADM_0A",
        id: 1,
        level: 0,
        levelName: "ADM_0",
        name: "ADM_0A",
        parent: null,
        path: null,
      },
    ];

    const bounds = geo.getBounds(administration);
    expect(typeof bounds).toBe("object");
    expect(bounds).toHaveProperty("coordinates");
  });
  test("defaultPos", () => {
    expect(typeof geo.defaultPos()).toBe("object");
  });
  test("check geo Object", () => {
    expect(geo).toHaveProperty("geojson");
    expect(geo).toHaveProperty("shapeLevels");
    expect(geo).toHaveProperty("tile");
    expect(geo).toHaveProperty("getBounds");
    expect(geo).toHaveProperty("defaultPos");
    expect(geo).toMatchSnapshot();
  });
});
