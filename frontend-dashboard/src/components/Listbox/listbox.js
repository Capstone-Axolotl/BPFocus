import * as React from 'react';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import data from './../Network/data.json'
import styles from './listbox.css'
import { styled } from '@mui/material/styles';

export default function ComboBox() {
    const [value, setValue] = React.useState(null);
    const [inputValue, setInputValue] = React.useState('');  
    
  return (
    <div>
      <h1>{value !== null ? `${value.name}` : ''}{' Performance'}</h1>
        {/* <div>{`value: ${value !== null ? `'${value.name}'` : 'null'}`}</div>
        <div>{`inputValue: '${inputValue}'`}</div> */}
    <div>
    <div className='box'>
      <Autocomplete className='drop'
    value={value}
    onChange={(event, newValue) => {
      setValue(newValue);
      localStorage.setItem("value", JSON.stringify(newValue));
    }}
    inputValue={inputValue}
    onInputChange={(event, newInputValue) => {
      setInputValue(newInputValue);
    }}
      disablePortal
      id="combo-box"
      getOptionLabel={(user) => user.name}
      options={data.nodes}
      sx={{ width: 250}}
      renderInput={(params) => <TextField {...params} label="name"/>}
      />
    </div>
   
      <div className='info'>
        {/* <p>{'Name  :    '}{value !== null ? `${value.name}` : ''}</p> */}
        <>{'E-mail :    '}{value !== null ? `${value.email}` : ''}</>
      </div>
    </div>
    </div>
  );
}