// eslint-disable-next-line no-unused-vars
import React, { useEffect, useState } from 'react';

const Home = () => {
    const [htmlContent, setHtmlContent] = useState('');

    useEffect(() => {
        const fetchHtml = async () => {
            try {
                const response = await fetch(`${process.env.REACT_APP_API_URL}/notes`);
                const data = await response.json();
                setHtmlContent(data.html);
            } catch (error) {
                console.error('Error fetching HTML:', error);
            }
        };

        fetchHtml();
    }, []);

    return (
        <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
    );
};

export default Home;
