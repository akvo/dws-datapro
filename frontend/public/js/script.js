const updateOffset = () => {
  requestAnimationFrame(updateOffset);
  if (document.querySelector(".js-content")) {
    document.body.style.setProperty(
      "--y",
      document.querySelector(".js-content").scrollTop
    );
  }
  updateProps();
};

const updateProps = () => {
  let i = -1;
  const viewportHeight = window.innerHeight;

  // Handle blocks
  for (let block of document.querySelectorAll(".block")) {
    i += 1;
    const rect = block.getBoundingClientRect();
    const top = rect.top;
    const isInView =
      top < viewportHeight * 0.85 && rect.bottom > viewportHeight * 0.15;

    if (isInView) {
      block.classList.add("is-visible");
    }

    if (top < viewportHeight * 1.3 && top > viewportHeight * -1.3) {
      document.body.style.setProperty(`--yBlock-${i + 1}`, top);
    } else {
      document.body.style.setProperty(`--yBlock-${i + 1}`, 0);
    }
  }

  // Handle grid items separately for fade-in
  for (let item of document.querySelectorAll(".img-gridItem")) {
    const rect = item.getBoundingClientRect();
    const top = rect.top;
    const isInView =
      top < viewportHeight * 0.9 && rect.bottom > viewportHeight * 0.1;

    if (isInView) {
      item.classList.add("is-visible");
    }
  }
};

updateProps();
updateOffset();
