import { useModal } from "../../context/Modal";

export default function OpenModalMenuItem({
  itemText,
  modalComponent,
  onItemClick,
  className = "",
}) {
  const { setModalContent, setOnModalClose } = useModal();

  const handleClick = () => {
    if (onItemClick) onItemClick();
    setModalContent(modalComponent);
    setOnModalClose(null);
  };

  return (
    <button
      type="button"
      className={`open-modal-trigger ${className}`}
      onClick={handleClick}
    >
      {itemText}
    </button>
  );
}
