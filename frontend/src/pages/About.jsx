function About() {
  return (
    <main className="about">
      <div className="about-container">
        
        {/* LEFT */}
        <section className="about-story">
          <h1>Our Story</h1>
          <p>
            We are a team of students and audio-technology enthusiasts who noticed
            a growing problem: it is becoming harder for people to understand
            whether a voice recording is real or artificially generated.
          </p>

          <p>
            We combined our experience in machine learning, speech processing,
            and signal analysis to build a system capable of detecting signs of
            artificial generation, manipulation, and inconsistencies in voice recordings.
          </p>

          <p>
            Today, we continue improving our models, expanding our datasets,
            and making technology honest, transparent, and helpful.
          </p>
        </section>

        {/* RIGHT */}
        <section className="about-right">
          <div className="about-image" />

          <div className="stats">
            <div className="stat">
              <strong>100000</strong>
              <span>Audio files analyzed</span>
            </div>

            <div className="stat">
              <strong>3</strong>
              <span>AI models used</span>
            </div>

            <div className="stat">
              <strong>20000</strong>
              <span>Fake audios detected</span>
            </div>

            <div className="stat">
              <strong>4</strong>
              <span>Years of experience</span>
            </div>
          </div>
        </section>

      </div>
    </main>
  );
}

export default About;
