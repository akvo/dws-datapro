import React, { useEffect } from "react";
import "./style.scss";

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
      <section className="block section-jumbotron" style={{ height: "100vh" }}>
        <figure className="item-parallax-media ">
          <img
            src="https://images.unsplash.com/photo-1642450909999-7106494ef779?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
            alt="Water landscape"
            style={{
              height: "100vh",
              width: "100%",
              objectFit: "cover",
              objectPosition: "center",
              filter: "brightness(0.8)",
              position: "absolute",
              top: 0,
              left: 0,
              zIndex: -1,
              transition: "filter 0.3s ease-in-out",
            }}
          />
        </figure>
        <div className="item-parallax-content flex-container">
          <div className="landing-content centered-content">
            <span className="head-sm">Department of</span>
            <h1 className="head-2xl">Water & Sewerage</h1>
          </div>
        </div>
      </section>

      <section className="block section-container water-ripple-effects">
        <div className="item-parallax-content flex-container">
          <div className="centered-content">
            <h2 className="head-md head-centered">Our Mandate</h2>
            <p className="section-caption-text">
              The Department of Water and Sewerage is mandated with the
              responsibility of ensuring a sustainable water and sewerage sector
              through the development of innovative policies, efficient service
              delivery, and rigorous compliance monitoring.
            </p>
          </div>
        </div>
      </section>

      <section className="block">
        <figure className="item-parallax-media">
          <img
            src="https://images.unsplash.com/photo-1744157801849-5e090acbdf84?q=80&w=2089&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
            alt="Water resources"
            style={{
              width: "100%",
              height: "720px",
              objectFit: "cover",
              filter: "brightness(0.4)",
              position: "absolute",
              top: 0,
              left: 0,
              zIndex: -1,
            }}
          />
        </figure>
        <div className="item-parallax-content flex-container">
          <div className="centered-content section-container">
            <h1 className="head-xl head-centered">
              Our <br />
              Responsibilities
            </h1>
            <p className="section-caption-text">
              The key roles and responsibilities of the Department include
              policy and legislation development, technical and policy advisory,
              compliance monitoring, and Water Authority of Fiji oversight.
            </p>
          </div>
        </div>
      </section>

      <section className="block">
        <div className="item-parallax-content flex-container img-grid">
          <figure className="img-gridItem type-right">
            <img
              src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/46992/andrew-branch-139678.jpg"
              alt="Water policy"
            />
            <figcaption className="img-caption">
              <h2 className="head-sm">Policy &amp; Legislation</h2>
              <p className="copy copy-white">
                Formulating regulatory frameworks and policies to promote a
                sustainable water and sewerage sector. Providing expert advice
                on water and sewerage issues to support effective governance.
              </p>
            </figcaption>
          </figure>
          <figure className="img-gridItem type-left">
            <img
              src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/46992/peter-hershey-112799.jpg"
              alt="Compliance monitoring"
            />
            <figcaption className="img-caption">
              <h2 className="head-sm">Monitoring &amp; Oversight</h2>
              <p className="copy copy-white">
                Overseeing adherence to established policies, legislation, and
                industry standards. Serving as the primary government agency
                responsible for monitoring the activities of the Water Authority
                of Fiji.
              </p>
            </figcaption>
          </figure>
          <figure className="img-gridItem type-right">
            <img
              src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/46992/andrew-branch-139678.jpg"
              alt="Water policy"
            />
            <figcaption className="img-caption">
              <h2 className="head-sm">Policy &amp; Legislation</h2>
              <p className="copy copy-white">
                Formulating regulatory frameworks and policies to promote a
                sustainable water and sewerage sector. Providing expert advice
                on water and sewerage issues to support effective governance.
              </p>
            </figcaption>
          </figure>
          <figure className="img-gridItem type-left">
            <img
              src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/46992/peter-hershey-112799.jpg"
              alt="Compliance monitoring"
            />
            <figcaption className="img-caption">
              <h2 className="head-sm">Monitoring &amp; Oversight</h2>
              <p className="copy copy-white">
                Overseeing adherence to established policies, legislation, and
                industry standards. Serving as the primary government agency
                responsible for monitoring the activities of the Water Authority
                of Fiji.
              </p>
            </figcaption>
          </figure>
        </div>
      </section>

      {/* Change section to footer and add classes for styling */}
      <section className="block footer-section ">
        <div className="flex-container section-container">
          {/* Add column classes */}
          <div className="footer-column footer-column-1">
            <h1 className="head-xl">IWSIMS</h1>
            <p className="copy copy-white">
              The Fiji Integrated Water and Sewerage Information Management
              System (IWSIMS) is a comprehensive platform designed to enhance
              the management of water and sewerage services in Fiji. It serves
              as a centralized hub for data collection, analysis, and reporting,
              enabling informed decision-making and efficient resource
              allocation.
            </p>
          </div>
          {/* Add column classes */}
          <div className="footer-column footer-column-2 text-sm text-white/60">
            <div className="flex items-start mb-2">
              <div>
                Department of Water and Sewerage
                <br />
                Ministry of Public Works and Meteorological Services, and
                Transport
              </div>
            </div>
            <div className="flex items-start mb-2">
              <div>
                Private Mail Bag, Suva, Fiji
                <br />
                Level 4, Nasilivata House, Ratu Mara Road,
                <br />
                Samabula, Suva
              </div>
            </div>
            <div className="flex items-center">
              <span>(+679) 3384111</span>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
};

export default React.memo(Home);
