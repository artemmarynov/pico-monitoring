function About() {
  return (
    <main className="about">
      <div className="about-page">
        <section className="our-story">
          <h2>Our Story</h2>

          <p>
            The product was created for Bachelor's thesis at TUKE by Artem Marynov.
          </p>

          <p>
            The goal of the project is to monitor key environmental indicators such as
            temperature, humidity, and CO₂ levels in classrooms.
          </p>

          <p>The following improvements could be considered in future iterations:</p>

          <ul className="future-steps">
            <li>Enable administrator registration without direct involvement from existing admins.</li>
            <li>Introduce real-time notifications when environmental indicators reach unhealthy levels.</li>
            <li>Integrate the system with automation technologies such as smart windows or smart AC.</li>
            <li>Make the contact form fully functionable.</li>
          </ul>
        </section>
      </div>
    </main>
  );
}

export default About;
