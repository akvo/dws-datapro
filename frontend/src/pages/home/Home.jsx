import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import "./style.scss";
import { AkvoIcon } from "../../components/Icons";
import { config } from "../../lib";
import {
  quickLinks,
  jumbotron,
  mandate,
  structure,
  keyRoles,
  footer,
} from "./static";

const Home = () => {
  useEffect(() => {
    // Create a script element to load script.js
    const script = document.createElement("script");
    script.src = "/js/script.js";
    script.async = true;

    // Add the script to the document
    document.body.appendChild(script);

    // Clean up function to remove the script when component unmounts
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return (
    <main className="content js-content">
      <section className="block section-jumbotron">
        <figure className="item-parallax-media ">
          <img
            src={jumbotron.image.src}
            alt={jumbotron.image.alt}
            style={{
              height: "100vh",
              width: "100%",
              objectFit: "cover",
              objectPosition: "center",
              filter: "brightness(0.8)",
              position: "absolute",
              left: 0,
              zIndex: -1,
              transition: "filter 0.3s ease-in-out",
            }}
          />
        </figure>
        <div className="item-parallax-content flex-container">
          <div className="landing-content centered-content">
            <span className="head-title">{jumbotron.subtitle}</span>
            <h1 className="head-2xl">{jumbotron.title}</h1>
          </div>
        </div>
      </section>

      <section className="block">
        <div
          className="item-parallax-content centered-content section-container"
          style={{ paddingTop: 128, paddingBottom: 128 }}
        >
          <h1 className="head-md head-centered">{mandate.title}</h1>
          <p className="section-caption-text">{mandate.text}</p>
        </div>
        <div className="item-parallax-content flex-container img-grid">
          <figure className="img-gridItem type-left">
            <img src="/assets/department-structure.jpg" alt="Department" />
            <figcaption className="img-caption">
              <h2 className="head-title">{structure.title}</h2>
              <p className="copy copy-white">{structure.text}</p>
            </figcaption>
          </figure>
        </div>
      </section>

      <section className="block">
        <div
          className="centered-content section-container"
          style={{ paddingTop: 128, paddingBottom: 128 }}
        >
          <h1 className="head-md head-centered">{keyRoles.title}</h1>
          <p className="section-caption-text">{keyRoles.text}</p>
        </div>
        <div className="item-parallax-content flex-container img-grid">
          {keyRoles.items.map((item, index) => (
            <figure key={index} className={`img-gridItem type-${item.type}`}>
              <img src={item.imgSrc} alt={item.imgAlt} />
              <figcaption className="img-caption">
                <h2 className="head-title">{item.title}</h2>
                <p className="copy copy-white">{item.text}</p>
              </figcaption>
            </figure>
          ))}
        </div>
      </section>

      <section className="block footer-section ">
        <div className="flex-container section-container">
          <div className="footer-co</div>lumn footer-column-1">
            <div className="footer-logo-container">
              <Link to="/">
                <div className="footer-logo">
                  <img src={config.siteLogo} alt={config.siteLogo} />
                </div>
              </Link>
            </div>
          </div>
          <div className="footer-column footer-column-2 text-sm text-white/60">
            <h4 className="head-sm">{footer.quickLinksTitle}</h4>
            <ul className="quick-links-list">
              {quickLinks.map((link, index) => (
                <li key={index} className="mb-2">
                  <Link to={link.href} className="text-white/60">
                    {link.text}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          <div className="footer-column footer-column-2 text-sm text-white/60">
            <h4 className="head-sm">{footer.contactTitle}</h4>
            <div className="flex items-start mb-2">
              <div>
                {footer.contactDetails.map((line, index) => (
                  <React.Fragment key={index}>
                    {line}
                    <br />
                  </React.Fragment>
                ))}
              </div>
            </div>
            <div className="flex items-start mb-2">
              <div>
                {footer.contactAddress.map((line, index) => (
                  <React.Fragment key={index}>
                    {line}
                    <br />
                  </React.Fragment>
                ))}
              </div>
            </div>
            <div className="flex items-center">
              <a href={`tel:${footer.contactPhone.replace(/\(|\)|\s/g, "")}`}>
                <span>{footer.contactPhone}</span>
              </a>
            </div>
          </div>
          <div className="footer-column footer-column-2 text-sm text-white/60">
            <h4 className="head-sm">{footer.aboutTitle}</h4>
            <div className="flex items-start mb-2">
              <div>{footer.aboutText}</div>
            </div>
          </div>
        </div>
        <div className="footer-copyright">
          <div>
            <p className="copy copy-white">{footer.copyrightText}</p>
          </div>
          <div className="powered-by-container">
            <span className="copy copy-white">{footer.poweredByText}</span>
            <span>
              <AkvoIcon />
            </span>
          </div>
        </div>
      </section>
    </main>
  );
};

export default React.memo(Home);
