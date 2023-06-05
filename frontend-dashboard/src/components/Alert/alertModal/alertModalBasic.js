import styles from './alertModalBasic.module.css';
import React from "react";
import Chat from '../Alert';

function AlertModalBasic({ setAlertModalOpen, alertMessages }) {
  const closeModal = () => {
    setAlertModalOpen(false);
  };

  return (
    <div className={styles.container}>
      <button className={styles.close} onClick={closeModal}>
        X
      </button>
      <p>
        <Chat alertMessages={alertMessages} />
      </p>
    </div>
  );
}

export default AlertModalBasic;