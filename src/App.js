// import React from "react";
// // import { Document, Page, pdfjs } from "react-pdf";
// import PDF from "./assets/basic-link-1.pdf";
// // pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;
// const App = () => (
//   <iframe
//     title="pdf"
//     src={PDF + "#toolbar=0&navpanes=0&scrollbar=0"}
//     width="100%"
//     height="601px"
//     onContextMenu={(e) => e.preventDefault()}
//   ></iframe>
// );
// export default App;

import React from "react";
import { Document, Page, pdfjs } from "react-pdf";
import PDF from "./assets/basic-link-1.pdf";

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;

const App = () => (
  <Document
    file={PDF}
    onContextMenu={(e) => e.preventDefault()}
    className="pdf-container"
  >
    <Page pageNumber={1} />
  </Document>
);

export default App;
