import { useState } from "react";
import menu from './../menu.png'
import CmpModalBasic from './cmpModalBasic'
import styles from'./cmpModal.module.css'

function CmpModal() {
  // 모달창 노출 여부 state
  const [ModalOpen, setcmpModalOpen] = useState(false);

  // 모달창 노출
  const showcmpModal = () => {
      setcmpModalOpen(true);
  };

  return (
      <div>
          <button className={styles.opencmpmodal} onClick={showcmpModal}><img src={menu} width={30}/></button>
          {ModalOpen && <CmpModalBasic setcmpModalOpen={setcmpModalOpen} />}
      </div>
        
  );
}

export default CmpModal;