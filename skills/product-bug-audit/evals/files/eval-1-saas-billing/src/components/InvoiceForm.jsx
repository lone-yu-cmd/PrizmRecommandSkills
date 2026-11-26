import React, { useState } from 'react';

export function InvoiceForm({ onCreated }) {
  const [title, setTitle] = useState('');
  const [amount, setAmount] = useState('');
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    const savedTitle = title;
    const savedAmount = amount;
    setTitle('');
    setAmount('');

    try {
      const res = await fetch('/api/invoices', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: savedTitle, qty: 1, unitPrice: Number(savedAmount), taxRate: 0.1 }),
      });
      if (!res.ok) {
        setError('Failed to create invoice');
        return;
      }
      const data = await res.json();
      if (onCreated) onCreated(data);
    } catch (_err) {
      setError('Network error while creating invoice');
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <div role="alert">{error}</div>}
      <input name="title" value={title} onChange={(e) => setTitle(e.target.value)} />
      <input name="amount" value={amount} onChange={(e) => setAmount(e.target.value)} />
      <button type="submit">Create Invoice</button>
    </form>
  );
}
