import React, { useState, useEffect } from "react";

function App() {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [qrData, setQrData] = useState([]);
  const API_BASE = "http://localhost:8000";

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    const res = await fetch(`${API_BASE}/files`);
    const data = await res.json();
    setFiles(data.files);
  };

  const handleUpload = async (e) => {
    const formData = new FormData();
    formData.append("file", e.target.files[0]);
    await fetch(`${API_BASE}/upload`, { method: "POST", body: formData });
    fetchFiles();
  };

  const selectFile = async (file) => {
    setSelectedFile(file);
    const res = await fetch(`${API_BASE}/extract_qr/${file}`);
    const data = await res.json();
    setQrData(data.qr_data || []);
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <div style={{ width: "30%", padding: 10, borderRight: "1px solid #ccc" }}>
        <h3>Upload</h3>
        <input type="file" onChange={handleUpload} />
        <h3>PDF Utilities</h3>
        <button disabled>Split (placeholder)</button>
        <button disabled>Merge (placeholder)</button>
        <h3>Files</h3>
        <ul>
          {files.map((f) => (
            <li key={f}>
              <button onClick={() => selectFile(f)}>{f}</button>
            </li>
          ))}
        </ul>
      </div>

      <div style={{ width: "70%", padding: 10 }}>
        {selectedFile ? (
          <>
            <div style={{ height: "70%" }}>
              <embed
                src={`${API_BASE}/file/${selectedFile}`}
                width="100%"
                height="100%"
                type="application/pdf"
              />
            </div>
            <div style={{ height: "30%", borderTop: "1px solid #ccc", paddingTop: 5 }}>
              <h4>QR Data</h4>
              <ul>
                {qrData.map((d, idx) => (
                  <li key={idx}>{d}</li>
                ))}
              </ul>
            </div>
          </>
        ) : (
          <p>Select a file to preview</p>
        )}
      </div>
    </div>
  );
}

export default App;