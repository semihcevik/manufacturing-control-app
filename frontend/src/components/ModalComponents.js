// src/components/ModalComponents.js

import React from 'react';
import Modal from 'react-modal';

// Set the app element for accessibility
Modal.setAppElement('#root');

// Reusable Confirmation Modal component
export const ConfirmationModal = ({ isOpen, onRequestClose, onConfirm, action, itemName }) => (
  <Modal
    isOpen={isOpen}
    onRequestClose={onRequestClose}
    contentLabel="Confirm Action"
    className="modal"
    overlayClassName="modal-overlay"
  >
    <h2>Confirm {action}</h2>
    <p>Are you sure you want to {action} {itemName}?</p>
    <div className="modal-actions">
      <button className="action-btn" onClick={onConfirm}>Yes</button>
      <button className="action-btn" onClick={onRequestClose}>No</button>
    </div>
  </Modal>
);

// Reusable Success Modal component
export const SuccessModal = ({ isOpen, onRequestClose, message }) => (
  <Modal
    isOpen={isOpen}
    onRequestClose={onRequestClose}
    contentLabel="Success"
    className="modal"
    overlayClassName="modal-overlay"
  >
    <h2>Success</h2>
    <p>{message}</p>
    <button className="action-btn" onClick={onRequestClose}>OK</button>
  </Modal>
);
