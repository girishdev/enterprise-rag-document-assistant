import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL;

export default function Documents({ token }) {
  const [file, setFile] = useState(null);
  const [documents, setDocuments] = useState([]);

  async function loadDocuments() {
    const response = await fetch(`${API_URL}/documents`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();
    setDocuments(data);
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  async function uploadDocument() {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_URL}/documents`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (response.ok) {
      setFile(null);
      await loadDocuments();
      alert("Document uploaded successfully");
    }
  }

  async function deleteDocument(id) {
    const response = await fetch(`${API_URL}/documents/${id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      await loadDocuments();
    }
  }

  return (
    <div>
      <h2>Documents</h2>

      <input
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={uploadDocument}>
        Upload
      </button>

      <hr />

      {documents.map((document) => (
        <div key={document.id}>
          <strong>{document.original_filename}</strong>

          {" - "}

          {document.processing_status}

          <button
            onClick={() => deleteDocument(document.id)}
          >
            Delete
          </button>
        </div>
      ))}
    </div>
  );
}