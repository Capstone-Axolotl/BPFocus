import React, { useEffect, useState } from "react";
import moment from 'moment';
import axios from 'axios';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import ArrowBackIosRoundedIcon from '@mui/icons-material/ArrowBackIosRounded';
import ArrowForwardIosRoundedIcon from '@mui/icons-material/ArrowForwardIosRounded';
import name from './Namelist.json';
import data from './prev.json';

function SearchDates({ onStopFetching, setData, setCombinedData }) {
  const dateNow = new Date();
  const today = dateNow.toISOString().slice(0, 10);

  const [finish, setFinish] = useState(today);
  const [start, setStart] = useState(today);
  const [startDate, setStartDate] = useState(today);
  const [startTime, setStartTime] = useState(today);

  const postData = async () => {
    const url = 'http://localhost:5000/get_perform';
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      data: {
        s_date: start,
        f_date: finish
      }
    };
  
    try {
      const response = await axios.post(url, requestOptions.data, {
        headers: requestOptions.headers
      });
      return response.data; // returned data will be stored in useEffect's response variable
    } catch (error) {
      console.error(error);
    }
  };

  const dataSetting = async (data) => {
    try {
      const modifiedDataList = await Promise.all(
        name.map(async (nameData) => {
          const response =  data[nameData.id];
          if (Array.isArray(response)) {
            const modifiedData = response.map((item) => ({
              name: nameData.name,
              date: item.date,
              cpu: item.cpu,
              mem: item.memory,
              net_in: item.net_in,
              net_out: item.net_out
            }));
            return modifiedData;
          } else {
              return null; 
         }
        })
      );

      const filteredDataList = modifiedDataList.filter((data) => data !== null);
      return filteredDataList;
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      const response = await postData();
      const modifiedDataList = await dataSetting(response);
      setData(modifiedDataList);
    };

    fetchData();
  }, [start, finish]);

  const handleClick = () => {
    const searchDateTime = moment(`${startDate} ${startTime}`).format('YYYY-MM-DD HH:mm:ss');
    setStart(searchDateTime);
    setFinish(moment(searchDateTime).subtract(1, 'minute').format('YYYY-MM-DD HH:mm:ss'));
    onStopFetching();
  };

  const handleClickBack = () => {
    const previousMinute = moment(start).subtract(1, 'minute').format('YYYY-MM-DD HH:mm:ss');
    setStart(previousMinute);
    setFinish(moment(previousMinute).subtract(1, 'minute').format('YYYY-MM-DD HH:mm:ss'));
    onStopFetching();
  };

  const handleClickLater = () => {
    const nextMinute = moment(start).add(1, 'minute').format('YYYY-MM-DD HH:mm:ss');
    setStart(nextMinute);
    setFinish(moment(nextMinute).subtract(1, 'minute').format('YYYY-MM-DD HH:mm:ss'));
    onStopFetching();
  };


  return (
    <div>
      <Box sx={{ '& button': { m: 1 } }}>
        <TextField
          className="date"
          id="date"
          label="검색 시작일"
          type="date"
          defaultValue={today}
          onChange={(e) => setStartDate(e.target.value)}
          inputProps={{ max: today }}
          InputLabelProps={{
            shrink: true,
          }}
        />
        <TextField
          id="date"
          label="검색 시작 시간"
          type="time"
          defaultValue={today}
          onChange={(e) => setStartTime(e.target.value)}
          inputProps={{ max: today }}
          InputLabelProps={{
            shrink: true,
          }}
        />
        
        <Button variant="contained" size="large" onClick={handleClick}>
          Search
        </Button>
      </Box>
      <Box sx={{ '& button': { m: 1 } }} >
        <IconButton aria-label="delete" onClick={handleClickBack}>
          <ArrowBackIosRoundedIcon  />
        </IconButton>
        <>{start}</>
        <IconButton aria-label="delete" onClick={handleClickLater}>
          <ArrowForwardIosRoundedIcon />
        </IconButton>
      </Box>
    </div>
  );
}

export default SearchDates;