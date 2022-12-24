from ethecycle.util.string_helper import quoted_join

addresses = """
  0x3a61da6d37493e2f248a6832f49b52af0a6f4fbb
  0xae2d4617c862309a3d75a0ffb358c7a5009c673f
  0xad6eaa735d9df3d7696fd03984379dae02ed8862
  0x561f551f0c65a14df1966e5d38c19d03b03263f5
  0xad6eaa735d9df3d7696fd03984379dae02ed8862
  0x87b49a99cbce4a9030e67919b776aa97d538adda
  0x2faf487a4414fe77e2327f0bf4ae2a264a776ad2
  0x28c6c06298d514db089934071355e5743bf21d60
  0xdfd5293d8e347dfe59e90efd55b2956a1343963d
  0x21a31ee1afc51d94c2efccaa2092ad1028285549
  0x3cd751e6b0078be393132286c442345e5dc49699
  0x3a61da6d37493e2f248a6832f49b52af0a6f4fbb
  0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43
  0x9696f59e4d72e237be84ffd425dcad154bf96976
  0x56eddb7aa87536c09ccc2793473599fd21a8b17f
  0xb5d85cbf7cb3ee0d56b3bb207d5fc4b82f43f511
  0x4af9842a0356e06a5f4a633422104e9dd20995e8
  0x561f551f0c65a14df1966e5d38c19d03b03263f5
  0x28c6c06298d514db089934071355e5743bf21d60
  0xdfd5293d8e347dfe59e90efd55b2956a1343963d
  0x21a31ee1afc51d94c2efccaa2092ad1028285549
  0x66c57bf505a85a74609d2c83e94aabb26d691e1f
  0x3a61da6d37493e2f248a6832f49b52af0a6f4fbb
  0xad6eaa735d9df3d7696fd03984379dae02ed8862
""".split()


query = 'SELECT * FROM wallets WHERE address LIKE '
query += quoted_join(addresses, separator='\n OR address LIKE ')
