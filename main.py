import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import json

ACCESS_TOKEN = "ory_at_4yynnDp1Mcejwmfk21nw2bImecOeSOZkRXx9vXPVIUM.r6WAesvO0rFu2S3vugLRHW30Btqktov-Vux1CZGer2I"
MEMPOOL_API_URL = "https://streaming.bitquery.io/graphql"
GRAPHQL_QUERY = """
{
  EVM(mempool: true) {
    Transactions(limit: {count: 200}) {
      Block {
        Time
        Number
      }
      Transaction {
        Hash
        Cost
        To
        From
      }
      Fee {
        Burnt
        SenderFee
        PriorityFeePerGas
        MinerReward
        GasRefund
        EffectiveGasPrice
        Savings
      }
    }
  }
}

"""


def fetch_data_from_mempool_api():
  headers = {
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {ACCESS_TOKEN}'
  }
  response = requests.post(MEMPOOL_API_URL, json={"query": GRAPHQL_QUERY}, headers=headers)
  data = response.json()
  return data['data']['EVM']['Transactions']


def main():
  st.title("Transaction Fee Analysis Dashboard")
  try:
    transactions_data = fetch_data_from_mempool_api()
  except Exception as e:
    st.error(f"Error fetching data from Mempool API: {str(e)}")

  block_time = []
  block_number = []
  transaction_hash = []
  transaction_cost = []
  transaction_to = []
  transaction_from = []
  fee_burnt = []
  fee_sender = []
  fee_priority = []
  fee_miner = []
  fee_refund = []
  fee_effective_gas = []
  fee_savings = []

  for transaction in transactions_data:
    block_time.append(transaction['Block']['Time'])
    block_number.append(transaction['Block']['Number'])
    transaction_hash.append(transaction['Transaction']['Hash'])
    transaction_cost.append(transaction['Transaction']['Cost'])
    transaction_to.append(transaction['Transaction']['To'])
    transaction_from.append(transaction['Transaction']['From'])
    fee_burnt.append(transaction['Fee']['Burnt'])
    fee_sender.append(transaction['Fee']['SenderFee'])
    fee_priority.append(transaction['Fee']['PriorityFeePerGas'])
    fee_miner.append(transaction['Fee']['MinerReward'])
    fee_refund.append(transaction['Fee']['GasRefund'])
    fee_effective_gas.append(transaction['Fee']['EffectiveGasPrice'])
    fee_savings.append(transaction['Fee']['Savings'])

  df = pd.DataFrame({
    'Block Time': block_time,
    'Block Number': block_number,
    'Transaction Hash': transaction_hash,
    'Transaction Cost': transaction_cost,
    'Transaction To': transaction_to,
    'Transaction From': transaction_from,
    'Fee Burnt': fee_burnt,
    'Fee Sender': fee_sender,
    'Fee Priority': fee_priority,
    'Fee Miner': fee_miner,
    'Fee Refund': fee_refund,
    'Fee Effective Gas': fee_effective_gas,
    'Fee Savings': fee_savings
  })

  st.subheader("Latest Transactions and Fee Details")
  st.write(df)

  timestamps = []
  burnt_fees = []
  priority_fees = []

  for transaction in transactions_data:
    timestamps.append(pd.to_datetime(transaction['Block']['Time']))
    burnt_fees.append(float(transaction['Fee']['Burnt']))
    priority_fees.append(float(transaction['Fee']['PriorityFeePerGas']))

  df = pd.DataFrame({
    'Timestamp': timestamps,
    'Burnt Fee': burnt_fees,
    'Priority Fee': priority_fees
  })

  df.set_index('Timestamp', inplace=True)

  st.subheader("Latest Transactions and Fee Details")
  st.write(df)

  st.subheader("Burnt Fee over Time")
  plt.figure(figsize=(10, 6))
  plt.scatter(df.index, df['Burnt Fee'], color='blue')
  plt.xlabel('Timestamp')
  plt.ylabel('Burnt Fee')
  plt.xticks(rotation=45)
  st.pyplot(plt)

  st.subheader("Priority Fee per Gas over Time")
  plt.figure(figsize=(10, 6))
  plt.scatter(df.index, df['Priority Fee'], color='red')
  plt.xlabel('Timestamp')
  plt.ylabel('Priority Fee per Gas')
  plt.xticks(rotation=45)
  st.pyplot(plt)
  return

if __name__ == "__main__":
  main()
