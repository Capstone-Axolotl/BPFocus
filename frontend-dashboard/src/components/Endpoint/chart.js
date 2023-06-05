import React, { useEffect, useState } from 'react';
import Chart from "react-apexcharts";
import axios from 'axios';
import './chart.css'

  const Stream = () => {
    const [cpu, setCpu] = useState([]);
    const [date, setDate] = useState([]);
    const [mem, setMem] = useState([]);
    const[net, setNet] = useState([]);
    const[netout, setNetOut] = useState([]);
    
    
    
  useEffect(() => {
    const fetchData = async () => {
      var selected = JSON.parse(localStorage.getItem('value'))
      try { 
        const response = await axios.get('http://localhost:8000/' + selected.id);
        if (Array.isArray(response.data)) {
          const modifiedData = response.data.map((item) => item.date.slice(10, 20));
          const modifiedCpu = response.data.map((item) => item.cpu);
          const modifiedMem = response.data.map((item) => item.memory);
          const modifiedNet = response.data.map((item) => item.net_in);
          const modifiedNetout = response.data.map((item) => item.net_out);
          setDate(modifiedData);
          setCpu(modifiedCpu);
          setMem(modifiedMem);
          setNet(modifiedNet);
          setNetOut(modifiedNetout);

        } else {
          setDate([]);
          setCpu([]);
          setMem([]);
          setNet([]);
          setNetOut([]);
        }
      } catch (error) {
        console.error(error);
      }
    };

    fetchData();

    const interval = setInterval(() => {
      fetchData();
    }, 1000);

    return () => clearInterval(interval);
  }, []);
   const series = [ //data on the y-axis
      {
        name: "cpu",
        data: [...cpu].reverse()
      },{
        name: "memory",
        data: [...mem].reverse()
      },{
        name: "network_in",
        data: [...net].reverse()
      },{
        name: "network_out",
        data: [...netout].reverse()
      }
    ];

    const options = {
      xaxis: {
        categories: [...date].reverse()
      },
      dataLabels: {
        enabled: false
      },
      chart: {
        toolbar: {
          show: false,
        }
        
      },
      colors: ["#000000", "#FF0000","#00FF00", "#0000FF"],
      grid: {
        show: false
      },
      stroke: {
        width: 0
      },
      tooltip: {
      enabled: true,
      enabledOnSeries: undefined,
      shared: true,
      followCursor: false,
      intersect: false,
      inverseOrder: false,
      custom: undefined,
      fillSeriesColor: false,
      theme: false
      },
      marker:{
        foreColor: "#000000"
      }
    }
  
    return (
      <div className='stream'>
        <Chart
          options={options}
          series={series}
          type="area"
          width="750"
          height="400"
        />
        <div>
          {/* {JSON.stringify(date)} */}
          
      {/* { result.isLoading && 'loading' }
      { result.error && 'error' }
      { result.data && result.data.name } */}
    </div>
      </div>
    )
  }
  
  export default Stream;