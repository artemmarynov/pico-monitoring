import { useState } from "react";

function Contacts() {
  const [form, setForm] = useState({
    name: "",
    phone: "",
    email: "",
    message: "",
  });

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((s) => ({ ...s, [name]: value }));
  };

  const onSubmit = (e) => {
    e.preventDefault();
    // Пока без backend — просто заглушка
    alert("Message sent (demo).");
    setForm({ name: "", phone: "", email: "", message: "" });
  };

  return (
    <main className="contacts">
      <div className="contacts-container">
        {/* TOP ROW */}
        <section className="contacts-top">
          <h1 className="contacts-title">CONTACT US</h1>
          <p className="contacts-subtitle">
            If you have any questions, feel free to contact us by phone, email,
            the form below, or any of our social media channels.
          </p>
        </section>

        {/* CARDS GRID */}
        <section className="contacts-grid">
          {/* LEFT: FORM */}
          <div className="card card-form">
            <div className="card-head">
              <h2 className="card-title">CONTACT FORM</h2>
              <div className="card-rule" />
            </div>

            <form className="form" onSubmit={onSubmit}>
              <div className="form-row">
                <label className="field">
                  <span className="field-label">NAME</span>
                  <input
                    className="input"
                    name="name"
                    value={form.name}
                    onChange={onChange}
                    placeholder="Enter your name*"
                    required
                  />
                </label>

                <label className="field">
                  <span className="field-label">PHONE NUMBER</span>
                  <input
                    className="input"
                    name="phone"
                    value={form.phone}
                    onChange={onChange}
                    placeholder="Enter your phone number*"
                    required
                  />
                </label>
              </div>

              <label className="field">
                <span className="field-label">EMAIL</span>
                <input
                  className="input input-wide"
                  name="email"
                  value={form.email}
                  onChange={onChange}
                  placeholder="Enter your email*"
                  type="email"
                  required
                />
              </label>

              <label className="field">
                <span className="field-label">YOUR MESSAGE</span>
                <textarea
                  className="textarea"
                  name="message"
                  value={form.message}
                  onChange={onChange}
                  placeholder=""
                  rows={5}
                  required
                />
              </label>

              <button className="btn btn-primary" type="submit">
                SEND MESSAGE
              </button>
            </form>
          </div>

          {/* RIGHT: INFO + HOURS */}
          <div className="right-col">
            {/* Contact information */}
            <div className="card card-info">
              <div className="card-head">
                <h2 className="card-title">CONTACT INFORMATION</h2>
                <div className="card-rule" />
              </div>

              <div className="info-grid">
                <div className="info-item">
                  <span className="info-icon">📞</span>
                  <div>
                    <div className="info-label">PHONE</div>
                    <div className="info-value">+421 965 785 544</div>
                  </div>
                </div>

                <div className="info-item">
                  <span className="info-icon">📍</span>
                  <div>
                    <div className="info-label">ADDRESS</div>
                    <div className="info-value">Letná 1/9, 040 01 Košice</div>
                  </div>
                </div>

                <div className="info-item">
                  <span className="info-icon">✉️</span>
                  <div>
                    <div className="info-label">EMAIL</div>
                    <div className="info-value">contact@deepvoicecheck.com</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Business hours */}
            <div className="card card-hours">
              <div className="card-head">
                <h2 className="card-title">BUSINESS HOURS</h2>
                <div className="card-rule" />
              </div>

              <div className="hours-grid">
                <div className="hours-item">
                  <div className="hours-day">MONDAY - FRIDAY</div>
                  <div className="hours-time">9:00 am–8:00 pm</div>
                </div>

                <div className="hours-item">
                  <div className="hours-day">SATURDAY</div>
                  <div className="hours-time">9:00 am–6:00 pm</div>
                </div>

                <div className="hours-item">
                  <div className="hours-day">SUNDAY</div>
                  <div className="hours-time">9:00 am–5:00 pm</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* MAP */}
        <section className="map-section">
          <iframe
            title="OpenStreetMap"
            className="map-frame"
            loading="lazy"
            src="https://www.openstreetmap.org/export/embed.html?bbox=21.240%2C48.716%2C21.265%2C48.724&layer=mapnik&marker=48.719%2C21.251"
          />
        </section>
      </div>
    </main>
  );
}

export default Contacts;
