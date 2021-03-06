
 PARAMETER NAME = C:\export\uaphysics\atlas\a7_mmfe_xadc_udp_v2\a7_mmfe_xadc_udp_v2.sdk\toplevel_bsp_0\system.mss

 PARAMETER VERSION = 2.2.0


BEGIN OS
 PARAMETER OS_NAME = standalone
 PARAMETER OS_VER = 4.2
 PARAMETER PROC_INSTANCE = microblaze_0
 PARAMETER stdin = mdm_1
 PARAMETER stdout = mdm_1
END


BEGIN PROCESSOR
 PARAMETER DRIVER_NAME = cpu
 PARAMETER DRIVER_VER = 2.2
 PARAMETER HW_INSTANCE = microblaze_0
END


BEGIN DRIVER
 PARAMETER DRIVER_NAME = axiethernet
 PARAMETER DRIVER_VER = 4.3
 PARAMETER HW_INSTANCE = axi_ethernet_0_eth_buf
END

BEGIN DRIVER
 PARAMETER DRIVER_NAME = llfifo
 PARAMETER DRIVER_VER = 4.0
 PARAMETER HW_INSTANCE = axi_ethernet_0_fifo
END

BEGIN DRIVER
 PARAMETER DRIVER_NAME = tmrctr
 PARAMETER DRIVER_VER = 3.0
 PARAMETER HW_INSTANCE = axi_timer_0
END

BEGIN DRIVER
 PARAMETER DRIVER_NAME = uartlite
 PARAMETER DRIVER_VER = 3.0
 PARAMETER HW_INSTANCE = mdm_1
END

BEGIN DRIVER
 PARAMETER DRIVER_NAME = intc
 PARAMETER DRIVER_VER = 3.2
 PARAMETER HW_INSTANCE = microblaze_0_axi_intc
END

BEGIN DRIVER
 PARAMETER DRIVER_NAME = bram
 PARAMETER DRIVER_VER = 4.0
 PARAMETER HW_INSTANCE = microblaze_0_local_memory_dlmb_bram_if_cntlr
END

BEGIN DRIVER
 PARAMETER DRIVER_NAME = bram
 PARAMETER DRIVER_VER = 4.0
 PARAMETER HW_INSTANCE = microblaze_0_local_memory_ilmb_bram_if_cntlr
END

BEGIN DRIVER
 PARAMETER DRIVER_NAME = sysmon
 PARAMETER DRIVER_VER = 7.0
 PARAMETER HW_INSTANCE = xadc_wiz_0
END


BEGIN LIBRARY
 PARAMETER LIBRARY_NAME = lwip140
 PARAMETER LIBRARY_VER = 2.3
 PARAMETER PROC_INSTANCE = microblaze_0
 PARAMETER lwip_tcp = false
 PARAMETER mem_size = 6000
 PARAMETER memp_n_pbuf = 8
 PARAMETER memp_n_tcp_pcb = 8
 PARAMETER memp_n_tcp_pcb_listen = 4
 PARAMETER memp_n_tcp_seg = 32
 PARAMETER memp_n_udp_pcb = 2
 PARAMETER memp_num_api_msg = 8
 PARAMETER memp_num_netbuf = 4
 PARAMETER memp_num_netconn = 8
 PARAMETER memp_num_tcpip_msg = 32
 PARAMETER pbuf_pool_bufsize = 400
 PARAMETER pbuf_pool_size = 64
 PARAMETER phy_link_speed = CONFIG_LINKSPEED100
 PARAMETER tcp_queue_ooseq = 0
 PARAMETER tcp_snd_buf = 1024
END


