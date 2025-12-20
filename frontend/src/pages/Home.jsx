import { useState, useEffect, useRef } from "react";
import { useLocation, useNavigationType } from "react-router-dom";

function Home() {
  const [step, setStep] = useState("upload"); // upload | preview | loading | result | save
  const [file, setFile] = useState(null);

  const location = useLocation();
  const navigationType = useNavigationType();
  const firstRender = useRef(true);

  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }

    if (location.pathname === "/" && navigationType === "PUSH") {
      setStep("upload");
      setFile(null);
    }
  }, [location.key]);

  /* FILE HANDLERS */

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;
    setFile(selectedFile);
    setStep("preview");
  };

  const handleAnalyze = () => {
    setStep("loading");
    setTimeout(() => setStep("result"), 3000);
  };

  const handleSaveResult = () => {
    setStep("save");
  };

  const handleSaveToDisk = async () => {
    try {
      const fileHandle = await window.showSaveFilePicker({
        suggestedName: "deepfake_result.txt",
        types: [
          {
            description: "Text file",
            accept: { "text/plain": [".txt"] },
          },
        ],
      });

      const writable = await fileHandle.createWritable();

      await writable.write(
        `Deepfake analysis result\n\nFile: ${file?.name}\nProbability: 73%\nStatus: Possible artificial generation`
      );

      await writable.close();

      setStep("upload");
      setFile(null);
    } catch (e) {
      if (e.name !== "AbortError") {
        alert("Saving failed");
      }
    }
  };

  return (
    <main className="main">
      <div className="main-inner">

        {/* LEFT TEXT */}
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

        {/* RIGHT CARD */}
        <section className="upload-card">

          {step === "upload" && (
            <>
              <h3>Please upload your file</h3>
              <p className="upload-hint">
                Select file, mp4, wav<br />
                Max file 5 Gb
              </p>

              <div className="file-icon">
                <img src="/load_file.png" alt="Upload" />
              </div>

              <input
                type="file"
                hidden
                id="fileInput"
                accept=".wav,.mp4"
                onChange={handleFileSelect}
              />

              <button
                className="btn-primary"
                onClick={() => document.getElementById("fileInput").click()}
              >
                Choose file
              </button>
            </>
          )}

          {step === "preview" && (
            <>
              <div className="file-icon">
                <img src="/load_file.png" alt="Preview" />
              </div>

              <h3>File selected</h3>
              <p>
                {file.name}<br />
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>

              <button className="btn-primary" onClick={handleAnalyze}>
                Analyze
              </button>
            </>
          )}

          {step === "loading" && (
            <>
              <div className="spinner" />
              <p>Analyzing audio…</p>
            </>
          )}

          {step === "result" && (
            <>
              <div className="file-icon">
                <img src="/load_file.png" alt="Result" />
              </div>

              <h3>Detailed result</h3>
              <p>
                Possible artificial generation<br />
                Probability: <b>73%</b>
              </p>

              <button className="btn-primary" onClick={handleSaveResult}>
                Save result
              </button>
            </>
          )}

          {step === "save" && (
            <>
              <div className="file-icon">
                <img src="/load_file.png" alt="Save" />
              </div>

              <h3>Choose where to save the result</h3>
              <p>The file will be saved to your computer</p>

              <div className="save-actions">
                <button className="btn-primary" onClick={handleSaveToDisk}>
                  Choose save location
                </button>

                <button
                  className="btn-ghost"
                  onClick={() => {
                    setStep("upload");
                    setFile(null);
                  }}
                >
                  Select another file
                </button>
              </div>
            </>
          )}

        </section>
      </div>
    </main>
  );
}

export default Home;
