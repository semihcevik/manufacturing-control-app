// src/components/PartManufacturing.js

import React, { useEffect, useState } from 'react';
import '../styles/PlaneManufacturing.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faRecycle } from '@fortawesome/free-solid-svg-icons';
import { fetchPartList, addPart, recyclePart } from '../services/partManufactureService';
import { ConfirmationModal, SuccessModal } from './ModalComponents'; // Import shared modal components

const PartManufacturing = ({ token }) => {
  const [parts, setParts] = useState([]);
  const [partId, setPartId] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [modalProps, setModalProps] = useState({
    isOpen: false,
    action: '',
    part: null,
  });
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await fetchPartList(token);
        if (response && response.data) {
          setPartId(response.part_id);
          setParts(response.data);
        } else {
          throw new Error('Invalid response structure');
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [token]);

  const openModal = (part, action) => {
    setModalProps({ isOpen: true, action, part });
  };

  const closeModal = () => {
    setModalProps({ isOpen: false, action: '', part: null });
  };

  const handleModalAction = async () => {
    const { action, part } = modalProps;
    if (!part || !partId) return;

    try {
      const result =
        action === 'add'
          ? await addPart(partId, part.plane_id, token)
          : await recyclePart(partId, part.plane_id, token);

      setSuccessMessage(result.message);

      // Update the part count in the table
      if (result.new_inventory !== undefined) {
        setParts((prevParts) =>
          prevParts.map((p) =>
            p.plane_id === result.plane_id ? { ...p, part_count: result.new_inventory } : p
          )
        );
      }

      closeModal();
    } catch (err) {
      setError(err.message);
    }
  };

  const closeSuccessModal = () => {
    setSuccessMessage('');
  };

  if (loading) {
    return <p>Loading part data...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  if (parts.length === 0) {
    return <p>No part data available.</p>;
  }

  return (
    <div className="part-manufacturing">
      <h2>Part Manufacturing Inventory</h2>
      <table className="plane-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Plane Name</th>
            <th>Part Count</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {parts.map((part) => (
            <tr key={part.plane_id}>
              <td>{part.plane_id}</td>
              <td>{part.plane_name}</td>
              <td>{part.part_count}</td>
              <td>
                <button className="action-btn" onClick={() => openModal(part, 'add')}>
                  <FontAwesomeIcon icon={faPlus} />
                </button>
                <button className="action-btn" onClick={() => openModal(part, 'recycle')}>
                  <FontAwesomeIcon icon={faRecycle} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <ConfirmationModal
        isOpen={modalProps.isOpen}
        onRequestClose={closeModal}
        onConfirm={handleModalAction}
        action={modalProps.action}
        itemName={modalProps.part?.plane_name}
      />

      <SuccessModal
        isOpen={!!successMessage}
        onRequestClose={closeSuccessModal}
        message={successMessage}
      />
    </div>
  );
};

export default PartManufacturing;
