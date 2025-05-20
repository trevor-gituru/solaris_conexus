'use client';

import React, { useEffect, useState } from 'react';
import { getContract } from '../../lib/stcContract';

const ContractReader = () => {
  const [balance, setBalance] = useState<string | null>(null);

  useEffect(() => {
    const fetchBalance = async () => {
      try {
        const contract = await getContract();
        const response = await contract.balanceOf("0x74de4a707539c4d01dd3d0e92c7a56c6974d2b8d5626f17deca161a32def42e");
        setBalance(response.toString());
      } catch (error) {
        console.error('Error reading contract:', error);
      }
    };

    fetchBalance();
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold">Contract Total Supply</h2>
      {balance ? (
        <p className="mt-2 text-lg text-gray-800">{balance}</p>
      ) : (
        <p className="mt-2 text-gray-500">Loading...</p>
      )}
    </div>
  );
};

export default ContractReader;

