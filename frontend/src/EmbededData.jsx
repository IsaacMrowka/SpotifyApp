import React from 'react';

const EmbededData = ({ results }) => {
  const trackLink = `https://open.spotify.com/embed/track/${results}?utm_source=generator`;

  return (
    <div>
      <iframe 
        src={trackLink} 
        width="75%" 
        height="100" 
        frameBorder="0" 
        allowFullScreen 
        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
        loading="lazy"
      ></iframe>
    </div>
  );
};

export default EmbededData;