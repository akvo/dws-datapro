export const generateAdvanceFilterURL = (advancedFilters, url) => {
  const queryUrlPrefix = url.includes("?") ? "&" : "?";
  const options = advancedFilters
    .map(({ id, label }) => {
      const query = encodeURIComponent(`${id}||${label.toLowerCase()}`);
      return `options=${query}`;
    })
    .join("&");
  url += `${queryUrlPrefix}${options}`;
  return url;
};

export const intersection = (array1, array2) => {
  const set1 = new Set(array1);
  const result = [];
  // eslint-disable-next-line no-restricted-syntax
  for (const item of array2) {
    if (set1.has(item)) {
      result.push(item);
    }
  }
  return result;
};

export const validateDependency = (dependency, value) => {
  if (dependency?.options && typeof value !== "undefined") {
    const v = typeof value === "string" ? [value] : value;
    return intersection(dependency.options, v)?.length > 0;
  }
  let valid = false;
  if (dependency?.min) {
    valid = value >= dependency.min;
  }
  if (dependency?.max) {
    valid = value <= dependency.max;
  }
  if (dependency?.equal) {
    valid = value === dependency.equal;
  }
  if (dependency?.notEqual) {
    valid = value !== dependency.notEqual && !!value;
  }
  return valid;
};
