import styles from './cmpMoalBasic.module.css'
import React from "react";
import MyListbox from '../Listbox/listbox';
import Stream from '../Endpoint/chart';
import InputValue from '../Listbox/inputName';

function cmpModalBasic({ setcmpModalOpen, id, title, content, writer }) {
    // 모달 끄기 
    const closeModal = () => {
        setcmpModalOpen(false);
    };

    return (
        <div className={styles.container}>
            <button className={styles.close} onClick={closeModal}>
                X
            </button>
            <p>
                <MyListbox/>
                <Stream/>
                <InputValue/>             
            </p>
        </div>
        
    );
}
export default cmpModalBasic;