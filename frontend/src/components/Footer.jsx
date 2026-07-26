import { useEffect, useState } from 'react';

function Footer() {
  const [companyName, setCompanyName] = useState('');

  useEffect(() => {
    fetch('http://localhost:8000/config')
      .then((res) => res.json())
      .then((data) => setCompanyName(data.company_name));
  }, []);

  return (
    <footer className="footer">
      <p>{companyName} &copy; {new Date().getFullYear()}</p>
    </footer>
  );
}

export default Footer;