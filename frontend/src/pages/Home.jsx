function Home() {
  return (
    <main className="main">
      <div className="main-inner">
        <section className="description">
          <p>
            Here you can check your audio recording for signs of deepfake
            manipulation. Our tool uses speech analysis methods and acoustic
            models to detect whether an audio file contains traces of artificial
            generation or editing. The service does not provide absolute
            guarantees, but it offers a careful probability estimate based on
            technical characteristics of the signal.
          </p>
        </section>

        <section className="upload-card">
          <div className="upload-left">
            <div className="file-icon" />

            <label>Choose model</label>
            <select className="model-select">
              <option>Wav 2 vec</option>
              <option>MFCC baseline</option>
              <option>X-vector</option>
            </select>
          </div>

          <div className="upload-right">
            <h3>Please upload your file</h3>
            <p>
              Select file: mp4, wav
              <br />
              Max file 5 GB
            </p>

            <button className="btn">Choose file</button>
          </div>
        </section>
      </div>
    </main>
  );
}

export default Home;
