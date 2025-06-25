import { store } from "../lib";

export const sortArray = (x, y) => {
  const nameOne = x.name.toLowerCase();
  const nameTwo = y.name.toLowerCase();
  if (nameOne < nameTwo) {
    return -1;
  }
  if (nameOne > nameTwo) {
    return 1;
  }
  return 0;
};

const filterFormByAssigment = (profile = {}) => {
  if (!Object.keys(profile).length) {
    return window.forms;
  }
  return profile.forms.length
    ? window.forms.filter((x) => profile.forms.map((f) => f.id).includes(x.id))
    : window.forms;
};

export const reloadData = (profile = {}, dataset = []) => {
  const filterForms = filterFormByAssigment(profile);
  const updatedForms = dataset.length
    ? filterForms.map((x) => {
        const newForm = dataset.find((d) => d.id === x.id);
        if (newForm) {
          return { ...x, ...newForm };
        }
        return x;
      })
    : filterForms;
  store.update((s) => {
    s.forms = updatedForms;
  });
};
