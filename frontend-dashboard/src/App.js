import React from 'react';
import Header from './components/header';
import NModal from './components/NewModal';
import CmpModal from './components/Button/cmpModal';
import data from './components/Network/data.json';
import { ForceGraph } from "./components/Network/forceGraph";
import './App.css';
import { useEffect, useState } from 'react';
import Chart from "react-apexcharts";
import axios from 'axios';

function App() {
  const updateName = async () => {
    const url = 'http://localhost:5000/disable_time';
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        
      })
    };

    try {
      const response = await axios.post(url, requestOptions.data, {
        headers: requestOptions.headers
      });
      console.log(response.data);
    } catch (error) {
      console.error(error);
    }
  };
  


  const [node, setNode] = useState([]);
  const [link, setLink] = useState([]);
  const [lengthNode, setLength] = useState(0);

useEffect(() => {
  const detectModify = async()=>{
    try {
      const noderesponse = await axios.get('http://localhost:7000/nodes');
      const linkresponse = await axios.get('http://localhost:7000/links');
      if (Array.isArray(noderesponse.data) && Array.isArray(linkresponse.data)) {
        if (noderesponse.status !== 304 || linkresponse.status !== 304) {
          const modifiedData = noderesponse.data;
          const modifiedTmp = linkresponse.data;
          setNode(modifiedData);
          setLink(modifiedTmp);
          setLength(Object.keys(modifiedData).length);
          updateName();
          localStorage.setItem('length', modifiedData.length);
        }
      } else {
        setNode([]);
        setLink([]);
      }
    } catch (error) {
      console.error(error);
    }
  }
  detectModify();
}, []); 



  const nodeHoverTooltip = React.useCallback((node) => {
    return `<div>     
      <b>${node.name}</b>
    </div>`;
  }, []);

  return (
    <div>
      <>{node.status}</>
    <Header/>
    <NModal/>    
    <CmpModal/>
    <section className="Main">
      <ForceGraph linksData={link} nodesData={node} nodeHoverTooltip={nodeHoverTooltip}/>
    </section>
    </div>
  );

  
}

export default App;