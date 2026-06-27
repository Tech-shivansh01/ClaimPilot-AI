"use client";

import { createContext, useContext, useState } from "react";

const ClaimDraftContext = createContext(null);

export function ClaimDraftProvider({ children }) {
  const [draftPhotos, setDraftPhotos] = useState([]);

  return (
    <ClaimDraftContext.Provider value={{ draftPhotos, setDraftPhotos }}>
      {children}
    </ClaimDraftContext.Provider>
  );
}

export function useClaimDraft() {
  return useContext(ClaimDraftContext);
}
