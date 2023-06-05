import { useState } from "react";
import styles from './alertModal.module.css';
import AlertModalBasic from './alertModalBasic';

function AlertModal({ messages }) {
  const [modalOpen, setAlertModalOpen] = useState(false);

  const showAlertModal = () => {
    setAlertModalOpen(true);
  };

  return (
    <div>
      <button className={styles.openalertmodal} onClick={showAlertModal}>open</button>
      {modalOpen && <AlertModalBasic setAlertModalOpen={setAlertModalOpen} alertMessages={messages} />}
      {messages}
    </div>
  );
}

export default AlertModal;