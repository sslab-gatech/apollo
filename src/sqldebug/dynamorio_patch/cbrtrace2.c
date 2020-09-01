#include "dr_api.h"
#include "drmgr.h"
#include "utils.h"

/* Application module */
static app_pc module_start_addr;
static app_pc module_end_addr;
static client_id_t client_id;
static int tls_idx;

/* For conditional branch, assuming ~20MB binary size */
int result_table[10000000] = {0}; // 0:nothing, 1:false, 2:true

/* Clean call for the cbr */
static void
at_cbr(app_pc inst_addr, app_pc targ_addr, app_pc fall_addr, int taken, void *bb_addr)
{   

    if (inst_addr < module_end_addr){        
        //false (not-taken)
        if (taken == 0){
            // if it is not true yet
            if (result_table[inst_addr-module_start_addr] !=2){
                result_table[inst_addr-module_start_addr] = 1;
            }
        } 
        
        //true (taken)
        else{
            result_table[inst_addr-module_start_addr] = 2;
        }
    }
}


static dr_emit_flags_t
event_app_instruction(void *drcontext, void *tag, instrlist_t *bb, instr_t *instr,
                      bool for_trace, bool translating, void *user_data)
{
    if (instr_is_cbr(instr)) {
        dr_insert_cbr_instrumentation_ex(drcontext, bb, instr, (void *)at_cbr,
                                         OPND_CREATE_INTPTR(dr_fragment_app_pc(tag)));
    }
    return DR_EMIT_DEFAULT;
}

static void
event_thread_init(void *drcontext)
{
    file_t log;
    log =
        log_file_open(client_id, drcontext, NULL /* using client lib path */, "cbrtf",
#ifndef WINDOWS
                      DR_FILE_CLOSE_ON_FORK |
#endif
                          DR_FILE_ALLOW_LARGE);
    DR_ASSERT(log != INVALID_FILE);
    drmgr_set_tls_field(drcontext, tls_idx, (void *)(ptr_uint_t)log);
}

static void
event_thread_exit(void *drcontext)
{
    file_t log = (file_t)(ptr_uint_t)drmgr_get_tls_field(drcontext, tls_idx);
    for (unsigned i = 0; i < module_end_addr - module_start_addr; ++i) {
        if (result_table[i] == 1){
            dr_fprintf(log, "%p:false\n", module_start_addr+i);
        } else if (result_table[i] == 2) {
            dr_fprintf(log, "%p:true\n", module_start_addr+i);
        }
    }

    log_file_close((file_t)(ptr_uint_t)drmgr_get_tls_field(drcontext, tls_idx));
}

static void
event_exit(void)
{
    dr_log(NULL, DR_LOG_ALL, 1, "Client 'cbrtrace' exiting");
#ifdef SHOW_RESULTS
    if (dr_is_notify_on())
        dr_fprintf(STDERR, "Client 'cbrtrace' exiting\n");
#endif
    if (!drmgr_unregister_bb_insertion_event(event_app_instruction) ||
        !drmgr_unregister_tls_field(tls_idx))
        DR_ASSERT(false);
    drmgr_exit();
}

DR_EXPORT
void
dr_client_main(client_id_t id, int argc, const char *argv[])
{
    dr_set_client_name("DynamoRIO Sample Client 'cbrtrace'", "http://dynamorio.org/issues");
    dr_log(NULL, DR_LOG_ALL, 1, "Client 'cbrtrace' initializing");
    drmgr_init();

    module_data_t *exe = dr_get_main_module();
    if (exe != NULL) {  
        module_start_addr = exe->start;
        for (unsigned i = 0; i < exe->num_segments; ++i) {
            module_segment_data_t   seg = exe->segments[i];
            if (seg.prot & DR_MEMPROT_EXEC) {
                module_end_addr = seg.end;                
            }
        }       
    }
    dr_free_module_data(exe);

    client_id = id;
    tls_idx = drmgr_register_tls_field();

    dr_register_exit_event(event_exit);
    if (!drmgr_register_thread_init_event(event_thread_init) ||
        !drmgr_register_thread_exit_event(event_thread_exit) ||
        !drmgr_register_bb_instrumentation_event(NULL, event_app_instruction, NULL))
        DR_ASSERT(false);

#ifdef SHOW_RESULTS
    if (dr_is_notify_on()) {
#    ifdef WINDOWS
        dr_enable_console_printing();
#    endif /* WINDOWS */
        dr_fprintf(STDERR, "Client 'cbrtrace' is running\n");
    }
#endif /* SHOW_RESULTS */
}
