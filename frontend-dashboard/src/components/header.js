import './../App.css';
import logo from './../axolotl.png';
import { useEffect, useState } from 'react';
import './header.css'
import './../App'

function Header(props){
    const [time, setTime] = useState(new Date());

    useEffect(() => {
      const id = setInterval(() => {
        setTime(new Date());
      }, 1000);
      return (() => clearInterval(id))
    }, []);
    return(
        <header className='header'>
            <img src={logo} className="App-logo" alt="logo" />
        <a>
          <span style={{fontFamily:'digital', fontSize:28, color:'white'}}>
            {time.toLocaleTimeString()}
          </span>
        </a>
        </header>
    )
}

export default Header