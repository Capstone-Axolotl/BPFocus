
import MyCharts from './Heatmap/heatmap';
import styles from './NModalBasic.module.css';

var data;
data = 20;

function ModalBasic({ setModalOpen, id, title, content, writer }) {
    // 모달 끄기 
    const closeModal = () => {
        setModalOpen(false);
    };

    return (
        <div className={styles.container}>
            <button className={styles.close} onClick={closeModal}>
                X
            </button>
            <h1>Heat map</h1>
            <MyCharts/>
            
        </div>
    );
}
export default ModalBasic;