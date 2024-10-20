// src/components/PlaneManufacturing.js

import React, { useEffect, useState } from 'react';
import '../styles/PlaneManufacturing.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faRecycle } from '@fortawesome/free-solid-svg-icons';
import {
  fetchPlaneList,
  assemblePlane,
  recyclePlane,
} from '../services/planeManufactureService';
import AssemblyHistory from './AssemblyHistory';
import { ConfirmationModal, SuccessModal } from './ModalComponents';

const PlaneManufacturing = ({ token }) => {
  const [planes, setPlanes] = useState([]);
  const [error, setError] = useState(null);
  const [modalProps, setModalProps] = useState({
    isOpen: false,
    action: '',
    plane: null,
  });
  const [successMessage, setSuccessMessage] = useState('');
  const [refreshHistory, setRefreshHistory] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const planeData = await fetchPlaneList(token);
        setPlanes(planeData);
      } catch (err) {
        setError(err.message);
      }
    };
    fetchData();
  }, [token]);

  const openModal = (plane, action) => {
    setModalProps({ isOpen: true, action, plane });
  };

  const closeModal = () => {
    setModalProps({ isOpen: false, action: '', plane: null });
  };

  const handleModalAction = async () => {
    const { action, plane } = modalProps;
    if (!plane) return;

    try {
      const result =
        action === 'assemble'
          ? await assemblePlane(plane.plane_id, token)
          : await recyclePlane(plane.plane_id, token);

      setSuccessMessage(result.message);

      if (result.new_inventory !== undefined) {
        setPlanes((prevPlanes) =>
          prevPlanes.map((p) =>
            p.plane_id === plane.plane_id ? { ...p, plane_inventory: result.new_inventory } : p
          )
        );
      }

      closeModal();
      setRefreshHistory((prev) => !prev);
    } catch (err) {
      setError(err.message);
    }
  };

  const closeSuccessModal = () => {
    setSuccessMessage('');
  };

  if (error) {
    return <p>{error}</p>;
  }

  if (planes.length === 0) {
    return <p>Loading plane data...</p>;
  }

  return (
    <div className="plane-manufacturing">
      <h2>Plane Manufacturing Inventory</h2>
      <table className="plane-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Plane Name</th>
            <th>Inventory</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {planes.map((plane) => (
            <tr key={plane.plane_id}>
              <td>{plane.plane_id}</td>
              <td>{plane.plane_name}</td>
              <td>{plane.plane_inventory}</td>
              <td>
                <button className="action-btn" onClick={() => openModal(plane, 'assemble')}>
                  <FontAwesomeIcon icon={faPlus} />
                </button>
                <button className="action-btn" onClick={() => openModal(plane, 'recycle')}>
                  <FontAwesomeIcon icon={faRecycle} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <AssemblyHistory token={token} refresh={refreshHistory} />

      <ConfirmationModal
        isOpen={modalProps.isOpen}
        onRequestClose={closeModal}
        onConfirm={handleModalAction}
        action={modalProps.action}
        itemName={modalProps.plane?.plane_name}
      />

      <SuccessModal
        isOpen={!!successMessage}
        onRequestClose={closeSuccessModal}
        message={successMessage}
      />
    </div>
  );
};

export default PlaneManufacturing;
