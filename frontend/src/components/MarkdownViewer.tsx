import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

interface MarkdownViewerProps {
  filename: string;
}

const MarkdownViewer: React.FC<MarkdownViewerProps> = ({ filename }) => {
  const [content, setContent] = useState<string | null>(null);

  useEffect(() => {
    fetch(`http://localhost:4000/api/markdowns/${filename}`)
      .then((res) => res.json())
      .then((data) => setContent(data.content))
      .catch((err) => console.error(err));
  }, [filename]);

  if (!content) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
};

export default MarkdownViewer;
