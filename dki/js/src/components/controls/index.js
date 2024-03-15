const requireComponent = require.context(".", false, /\.vue$/);

const components = {};

requireComponent.keys().forEach((fileName) => {
  const componentConfig = requireComponent(fileName);

  let componentName = fileName
    // Remove the "./_" from the beginning
    .replace(/^\.\//, "")
    // Remove the file extension from the end
    .replace(/\.\w+$/, "");

  componentName = componentName[0] + "x" + componentName.slice(2);
  components[componentName] = componentConfig.default || componentConfig;
});

export default components;
