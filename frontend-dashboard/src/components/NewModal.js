import { useState } from "react";
import ModalBasic from './NModalBasic'
import menu from './menu.png'
import './NModal.css'

function NModal() {
  // 모달창 노출 여부 state
  const [modalOpen, setModalOpen] = useState(false);

  // 모달창 노출
  const showModal = () => {
      setModalOpen(true);
  };

  return (
      <div>
          <button className="open-modal" onClick={showModal}><img src={menu} width={30}/></button>
          {modalOpen && <ModalBasic setModalOpen={setModalOpen} />}
      </div>
  );
}

export default NModal;