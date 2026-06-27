"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { useClaimDraft } from "../lib/ClaimDraftContext";
import RippleButton from "./RippleButton";

export default function PhotoDropzone() {
  const router = useRouter();
  const { draftPhotos, setDraftPhotos } = useClaimDraft();
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef(null);

  function addFiles(fileList) {
    const files = Array.from(fileList).filter((f) => f.type.startsWith("image/"));
    if (files.length > 0) {
      setDraftPhotos(files);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragActive(false);
    addFiles(e.dataTransfer.files);
  }

  return (
    <div>
      <div
        className={`dropzone ${dragActive ? "drag-active" : ""}`}
        onClick={() => inputRef.current.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
      >
        <span className="dz-icon">📸</span>
        <div className="dz-title">
          {draftPhotos.length > 0 ? `${draftPhotos.length} photo(s) selected` : "Drop an accident photo here"}
        </div>
        <div className="dz-sub">or click to browse — we'll carry it into your claim form</div>

        {draftPhotos.length > 0 && (
          <div className="dz-preview-row">
            {draftPhotos.slice(0, 4).map((file, i) => (
              <img key={i} src={URL.createObjectURL(file)} alt="preview" className="dz-thumb" />
            ))}
          </div>
        )}

        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          multiple
          style={{ display: "none" }}
          onChange={(e) => addFiles(e.target.files)}
        />
      </div>

      {draftPhotos.length > 0 && (
        <RippleButton className="btn-glow" style={{ marginTop: "12px" }} onClick={() => router.push("/submit-claim")}>
          Continue to claim form →
        </RippleButton>
      )}
    </div>
  );
}
